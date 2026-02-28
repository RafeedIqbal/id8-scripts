#!/usr/bin/env python3
"""Project-only installer for the /id8 multi-agent workflow."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MARKER_START = "# >>> id8-managed:start"
MARKER_END = "# <<< id8-managed:end"
GITIGNORE_MARKER_START = "# >>> id8-managed:gitignore:start"
GITIGNORE_MARKER_END = "# <<< id8-managed:gitignore:end"
VALID_AGENTS = ("claude", "codex", "antigravity")
VALID_AUTH_MODES = ("oauth", "key")

MCP_MANIFEST_RELATIVE_PATH = Path("assets/id8/mcp_manifest.json")


def toml_string(value: str) -> str:
    return json.dumps(value)


def toml_array(values: list[str]) -> str:
    encoded = ", ".join(toml_string(item) for item in values)
    return f"[{encoded}]"


def upsert_managed_block(
    existing_text: str,
    block_text: str,
    *,
    marker_start: str = MARKER_START,
    marker_end: str = MARKER_END,
) -> str:
    """Insert or replace a managed text block delimited by the given markers."""
    pattern = re.compile(
        rf"{re.escape(marker_start)}.*?{re.escape(marker_end)}\n?",
        flags=re.DOTALL,
    )
    if pattern.search(existing_text):
        return pattern.sub(block_text, existing_text)

    if existing_text and not existing_text.endswith("\n"):
        existing_text += "\n"
    if existing_text:
        existing_text += "\n"
    return existing_text + block_text


def build_codex_toml_block(entries: dict[str, dict[str, Any]]) -> str:
    lines: list[str] = [MARKER_START]
    for name, config in entries.items():
        lines.append(f"[mcp_servers.{name}]")
        lines.append(f"command = {toml_string(config['command'])}")
        lines.append(f"args = {toml_array(config['args'])}")
        if "enabled" in config:
            lines.append(f"enabled = {'true' if config['enabled'] else 'false'}")
        if "disabled" in config:
            lines.append(f"disabled = {'true' if config['disabled'] else 'false'}")
        if "disabledTools" in config:
            lines.append(f"disabledTools = {toml_array(config['disabledTools'])}")
        env = config.get("env")
        if isinstance(env, dict) and env:
            lines.append("")
            lines.append(f"[mcp_servers.{name}.env]")
            for env_key, env_value in env.items():
                lines.append(f"{env_key} = {toml_string(env_value)}")
        lines.append("")
    lines.append(MARKER_END)
    return "\n".join(lines) + "\n"


def parse_agents(value: str) -> list[str]:
    agents = [item.strip().lower() for item in value.split(",") if item.strip()]
    unique: list[str] = []
    for agent in agents:
        if agent not in VALID_AGENTS:
            raise ValueError(f"Invalid agent '{agent}'. Expected: {', '.join(VALID_AGENTS)}")
        if agent not in unique:
            unique.append(agent)
    if not unique:
        raise ValueError("No agents selected")
    return unique


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


class Installer:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.script_dir = Path(__file__).resolve().parent
        self.pending_auth: set[str] = set()
        self.manual_setup: list[str] = []
        self.changed_files: list[Path] = []
        self.backup_files: list[Path] = []
        self.warnings: list[str] = []
        self.info: list[str] = []
        self.mcp_servers = self._load_mcp_servers()

        self.project_dir = self._resolve_project_dir()
        self.agents = self._resolve_agents()
        self.antigravity_global_append = self._resolve_antigravity_global_append()
        self.vercel_auth_mode = self._resolve_auth_mode(
            service_name="Vercel",
            arg_value=self.args.vercel_auth,
            env_var="ID8_VERCEL_AUTH_MODE",
        )
        self.supabase_auth_mode = self._resolve_auth_mode(
            service_name="Supabase",
            arg_value=self.args.supabase_auth,
            env_var="ID8_SUPABASE_AUTH_MODE",
        )

    def run(self) -> int:
        self._check_dependencies()
        self._scaffold_project()
        self._write_assets()
        self._print_report()
        return 0

    def _scaffold_project(self) -> None:
        """Create id8-src/ (scaffolded Next.js app) and supabase/ in the project directory."""
        src_dir = self.project_dir / "id8-src"
        supabase_dir = self.project_dir / "supabase"

        if self.args.validate_only:
            self.info.append(f"[validate-only] Would create directory: {supabase_dir}")
        elif not supabase_dir.exists():
            supabase_dir.mkdir(parents=True, exist_ok=True)
            self.info.append(f"Created directory: {supabase_dir}")

        if src_dir.exists() and any(src_dir.iterdir()):
            self.info.append(f"Skipped Next.js scaffold: {src_dir} is not empty.")
            return

        if not command_exists("npx"):
            self.warnings.append("npx not found; skipping Next.js scaffold.")
            self.manual_setup.append(
                f"Run `npx create-next-app@latest id8-src --yes` in {self.project_dir} to scaffold the frontend."
            )
            return

        if self.args.validate_only:
            self.info.append(
                f"[validate-only] Would run: npx create-next-app@latest id8-src --yes in {self.project_dir}"
            )
            return

        print(f"\nScaffolding Next.js app in {src_dir}...")
        result = subprocess.run(
            ["npx", "create-next-app@latest", "id8-src", "--yes"],
            cwd=self.project_dir,
        )
        if result.returncode == 0:
            self.info.append(f"Scaffolded Next.js app at {src_dir}")
        else:
            self.warnings.append(
                f"create-next-app exited with code {result.returncode}; check output above."
            )
            self.manual_setup.append(
                f"Run `npx create-next-app@latest id8-src --yes` in {self.project_dir} to scaffold the frontend."
            )

    def _resolve_project_dir(self) -> Path:
        if self.args.project_dir:
            project = Path(self.args.project_dir).expanduser().resolve()
        elif self.args.non_interactive:
            raise ValueError("--project-dir is required when --non-interactive is set")
        else:
            entered = input(
                f"Project directory [{Path.cwd()}]: "
            ).strip() or str(Path.cwd())
            project = Path(entered).expanduser().resolve()

        if project.exists() and not project.is_dir():
            raise ValueError(f"Project path is not a directory: {project}")
        if not project.exists():
            if self.args.non_interactive and not self.args.force:
                raise ValueError(
                    f"Project directory does not exist: {project}. Use --force to create it."
                )
            if self.args.non_interactive or self._ask_yes_no(
                f"Create missing project directory {project}?",
                default=True,
            ):
                if self.args.validate_only:
                    self.info.append(f"[validate-only] Would create project directory: {project}")
                else:
                    project.mkdir(parents=True, exist_ok=True)
                    self.info.append(f"Created project directory: {project}")
            else:
                raise ValueError("Installer cancelled: project directory does not exist.")
        return project

    def _resolve_agents(self) -> list[str]:
        if self.args.agents:
            return parse_agents(self.args.agents)
        if self.args.non_interactive:
            raise ValueError("--agents is required when --non-interactive is set")
        default = "claude,codex,antigravity"
        raw = input(
            f"Select agents (comma separated: {', '.join(VALID_AGENTS)}) [{default}]: "
        ).strip() or default
        return parse_agents(raw)

    def _resolve_antigravity_global_append(self) -> bool:
        if "antigravity" not in self._peek_agents():
            return False

        env_override = os.getenv("ID8_APPEND_ANTIGRAVITY_GLOBAL_MCP")
        if env_override is not None:
            return env_override.strip().lower() in {"1", "true", "yes", "y"}

        if self.args.non_interactive:
            return False
        return self._ask_yes_no(
            "Append MCP servers to global Antigravity MCP list (~/.gemini/antigravity/mcp_config.json)?",
            default=False,
        )

    def _peek_agents(self) -> list[str]:
        if self.args.agents:
            return parse_agents(self.args.agents)
        return self.agents if hasattr(self, "agents") else []

    def _resolve_auth_mode(
        self,
        *,
        service_name: str,
        arg_value: str | None,
        env_var: str,
    ) -> str:
        if arg_value is not None:
            return self._validate_auth_mode(arg_value, source=f"--{service_name.lower()}-auth")

        env_value = os.getenv(env_var, "").strip().lower()
        if env_value:
            return self._validate_auth_mode(env_value, source=env_var)

        if self.args.non_interactive:
            return "oauth"

        return self._ask_choice(
            f"{service_name} auth mode",
            options=VALID_AUTH_MODES,
            default="oauth",
        )

    def _validate_auth_mode(self, value: str, *, source: str) -> str:
        normalized = value.strip().lower()
        if normalized not in VALID_AUTH_MODES:
            allowed = ", ".join(VALID_AUTH_MODES)
            raise ValueError(f"Invalid auth mode '{value}' from {source}. Expected one of: {allowed}")
        return normalized

    def _check_dependencies(self) -> None:
        if "claude" in self.agents and not command_exists("claude"):
            self.warnings.append("Claude CLI not found in PATH.")
            self._offer_install("claude")
        if "codex" in self.agents and not command_exists("codex"):
            self.warnings.append("Codex CLI not found in PATH.")
            self._offer_install("codex")
        if not command_exists("python3") and not command_exists("python"):
            self.warnings.append("Python runtime not found in PATH.")

    def _offer_install(self, tool: str) -> None:
        npm_ok = command_exists("npm")
        install_commands = {
            "claude": ["npm", "install", "-g", "@anthropic-ai/claude-code"],
            "codex": ["npm", "install", "-g", "@openai/codex"],
        }
        if not npm_ok:
            self.manual_setup.append(f"{tool}: npm is missing; install {tool} CLI manually.")
            return
        if self.args.non_interactive:
            self.manual_setup.append(
                f"{tool}: missing; non-interactive mode skipped automatic installation."
            )
            return
        if self._ask_yes_no(f"Attempt to install missing {tool} CLI using npm?", default=False):
            cmd = install_commands[tool]
            if self.args.validate_only:
                self.info.append(f"[validate-only] Would run: {' '.join(cmd)}")
                return
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.info.append(f"Installed {tool} CLI.")
            else:
                self.warnings.append(f"Failed to install {tool} CLI automatically.")
                self.manual_setup.append(f"{tool}: run {' '.join(cmd)} manually.")

    def _write_assets(self) -> None:
        substitutions = self._template_substitutions()

        if "claude" in self.agents:
            claude_skill = self._render_template(
                "assets/id8/templates/claude/SKILL.md.tmpl",
                substitutions | {"INVOCATION": "/id8"},
            )
            self._write_text_file(
                self.project_dir / ".claude/skills/id8/SKILL.md",
                claude_skill,
            )
            claude_mcp = self._build_claude_mcp_entries()
            self._write_json_mcp(self.project_dir / ".mcp.json", claude_mcp)

        if "codex" in self.agents:
            codex_skill = self._render_template(
                "assets/id8/templates/codex/SKILL.md.tmpl",
                substitutions | {"INVOCATION": "$id8"},
            )
            self._write_text_file(
                self.project_dir / ".agents/skills/id8/SKILL.md",
                codex_skill,
            )
            codex_block = build_codex_toml_block(self._build_codex_mcp_entries())
            self._write_toml_block(self.project_dir / ".codex/config.toml", codex_block)

        if "antigravity" in self.agents:
            workflow = self._render_template(
                "assets/id8/templates/antigravity/id8_workflow.md.tmpl",
                substitutions | {"INVOCATION": "/id8"},
            )
            rule = self._render_template(
                "assets/id8/templates/antigravity/id8_rule.md.tmpl",
                substitutions | {"INVOCATION": "/id8"},
            )
            self._write_text_file(self.project_dir / ".agent/workflows/id8.md", workflow)
            self._write_text_file(self.project_dir / ".agent/rules/id8.md", rule)

            if self.antigravity_global_append:
                antigravity_entries = self._build_antigravity_mcp_entries()
                self._write_json_mcp(
                    Path.home() / ".gemini/antigravity/mcp_config.json",
                    antigravity_entries,
                    url_key="serverUrl",
                )
            else:
                self.manual_setup.append(
                    "Antigravity MCP append skipped; configure ~/.gemini/antigravity/mcp_config.json manually."
                )

        self._write_env_example()
        self._write_gitignore()
        self._write_project_manifest()

    def _template_substitutions(self) -> dict[str, str]:
        return {
            "WORKFLOW_STEPS": self._load_text("assets/id8/workflow/id8_steps.md").strip(),
            "DRY_RUN_CHECKS": self._load_text("assets/id8/templates/common/dry_run_checks.md").strip(),
            "CONFIRMATION_GATES": self._load_text(
                "assets/id8/templates/common/confirmation_gates.md"
            ).strip(),
        }

    def _load_mcp_servers(self) -> dict[str, dict[str, str]]:
        manifest_path = self.script_dir / MCP_MANIFEST_RELATIVE_PATH
        manifest = self._load_json(manifest_path)
        servers = manifest.get("servers")
        if not isinstance(servers, dict):
            raise ValueError(f"Invalid MCP manifest at {manifest_path}: missing 'servers' object.")

        normalized: dict[str, dict[str, str]] = {}
        for name in ("context7", "stitch", "github", "vercel", "supabase"):
            server = servers.get(name)
            if not isinstance(server, dict):
                raise ValueError(f"Invalid MCP manifest at {manifest_path}: missing '{name}' server.")

            url = server.get("url")
            if not isinstance(url, str) or not url.strip():
                raise ValueError(
                    f"Invalid MCP manifest at {manifest_path}: server '{name}' has no valid 'url'."
                )

            entry: dict[str, str] = {"url": url}
            if name != "context7":
                header_key = server.get("header_key")
                secret_env_var = server.get("secret_env_var")
                if not isinstance(header_key, str) or not header_key.strip():
                    raise ValueError(
                        f"Invalid MCP manifest at {manifest_path}: server '{name}' has no valid "
                        "'header_key'."
                    )
                if not isinstance(secret_env_var, str) or not secret_env_var.strip():
                    raise ValueError(
                        f"Invalid MCP manifest at {manifest_path}: server '{name}' has no valid "
                        "'secret_env_var'."
                    )
                entry["header_key"] = header_key
                entry["secret_env_var"] = secret_env_var

            normalized[name] = entry

        return normalized

    def _mcp_url(self, server_name: str) -> str:
        return self.mcp_servers[server_name]["url"]

    def _mcp_secret_env_var(self, server_name: str) -> str:
        return self.mcp_servers[server_name]["secret_env_var"]

    def _mcp_auth_headers(self, server_name: str) -> dict[str, str]:
        header_key = self.mcp_servers[server_name]["header_key"]
        value = self._env_placeholder(self._mcp_secret_env_var(server_name))
        if header_key.lower() == "authorization":
            value = f"Bearer {value}"
        return {header_key: value}

    def _record_pending_auth(self) -> None:
        self.pending_auth.add("Context7: run OAuth/browser login in your MCP client.")
        self.pending_auth.add(
            f"Stitch: set {self._mcp_secret_env_var('stitch')} before launching your MCP client."
        )
        self.pending_auth.add(
            f"GitHub: set {self._mcp_secret_env_var('github')} before launching your MCP client."
        )
        if self.vercel_auth_mode == "key":
            self.pending_auth.add(
                f"Vercel: set {self._mcp_secret_env_var('vercel')} before launching your MCP client."
            )
        else:
            self.pending_auth.add("Vercel: run OAuth/browser login in your MCP client.")
        if self.supabase_auth_mode == "key":
            self.pending_auth.add(
                "Supabase: set "
                + f"{self._mcp_secret_env_var('supabase')} before launching your MCP client."
            )
        else:
            self.pending_auth.add("Supabase: run OAuth/browser login in your MCP client.")

    def _env_placeholder(self, env_var: str) -> str:
        return f"${{{env_var}}}"

    def _mcp_remote_args(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> list[str]:
        args = ["-y", "mcp-remote", url]
        if headers:
            for key, value in headers.items():
                args += ["--header", f"{key}: {value}"]
        return args

    def _vercel_headers(self) -> dict[str, str] | None:
        if self.vercel_auth_mode == "key":
            return self._mcp_auth_headers("vercel")
        return None

    def _supabase_headers(self) -> dict[str, str] | None:
        if self.supabase_auth_mode == "key":
            return self._mcp_auth_headers("supabase")
        return None

    def _build_claude_mcp_entries(self) -> dict[str, dict[str, Any]]:
        entries: dict[str, dict[str, Any]] = {
            "context7": {
                "type": "http",
                "url": self._mcp_url("context7"),
            },
            "stitch": {
                "type": "http",
                "url": self._mcp_url("stitch"),
                "headers": self._mcp_auth_headers("stitch"),
            },
            "github": {
                "type": "http",
                "url": self._mcp_url("github"),
                "headers": self._mcp_auth_headers("github"),
            },
            "vercel": {
                "type": "http",
                "url": self._mcp_url("vercel"),
            },
            "supabase": {
                "type": "http",
                "url": self._mcp_url("supabase"),
            },
        }

        vercel_headers = self._vercel_headers()
        if vercel_headers:
            entries["vercel"]["headers"] = vercel_headers

        supabase_headers = self._supabase_headers()
        if supabase_headers:
            entries["supabase"]["headers"] = supabase_headers
        self._record_pending_auth()
        return entries

    def _build_antigravity_mcp_entries(self) -> dict[str, dict[str, Any]]:
        entries: dict[str, dict[str, Any]] = {
            "context7": {
                "serverUrl": self._mcp_url("context7"),
            },
            "StitchMCP": {
                "$typeName": "exa.cascade_plugins_pb.CascadePluginCommandTemplate",
                "command": "npx",
                "args": self._mcp_remote_args(
                    self._mcp_url("stitch"),
                    headers=self._mcp_auth_headers("stitch"),
                ),
                "env": {},
            },
            "github-mcp-server": {
                "$typeName": "exa.cascade_plugins_pb.CascadePluginCommandTemplate",
                "command": "npx",
                "args": self._mcp_remote_args(
                    self._mcp_url("github"),
                    headers=self._mcp_auth_headers("github"),
                ),
                "env": {},
                "disabledTools": [],
            },
            "VercelMCP": {
                "$typeName": "exa.cascade_plugins_pb.CascadePluginCommandTemplate",
                "command": "npx",
                "args": self._mcp_remote_args(
                    self._mcp_url("vercel"),
                    headers=self._vercel_headers(),
                ),
                "env": {},
            },
            "supabase-mcp-server": {
                "$typeName": "exa.cascade_plugins_pb.CascadePluginCommandTemplate",
                "command": "npx",
                "args": self._mcp_remote_args(
                    self._mcp_url("supabase"),
                    headers=self._supabase_headers(),
                ),
                "env": {},
            },
        }

        self._record_pending_auth()
        return entries

    def _build_codex_mcp_entries(self) -> dict[str, dict[str, Any]]:
        entries: dict[str, dict[str, Any]] = {
            "context7": {
                "command": "npx",
                "args": self._mcp_remote_args(self._mcp_url("context7")),
                "enabled": True,
            },
            "StitchMCP": {
                "command": "npx",
                "args": self._mcp_remote_args(
                    self._mcp_url("stitch"),
                    headers=self._mcp_auth_headers("stitch"),
                ),
                "enabled": True,
            },
            "github_mcp_server": {
                "command": "npx",
                "args": self._mcp_remote_args(
                    self._mcp_url("github"),
                    headers=self._mcp_auth_headers("github"),
                ),
                "enabled": True,
            },
            "VercelMCP": {
                "command": "npx",
                "args": self._mcp_remote_args(
                    self._mcp_url("vercel"),
                    headers=self._vercel_headers(),
                ),
                "enabled": True,
            },
            "supabase_mcp_server": {
                "command": "npx",
                "args": self._mcp_remote_args(
                    self._mcp_url("supabase"),
                    headers=self._supabase_headers(),
                ),
                "enabled": True,
            },
        }

        self._record_pending_auth()
        return entries

    def _write_project_manifest(self) -> None:
        payload = {
            "project_dir": str(self.project_dir),
            "agents": self.agents,
            "antigravity_global_mcp_appended": self.antigravity_global_append,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "auth_modes": {
                "vercel": self.vercel_auth_mode,
                "supabase": self.supabase_auth_mode,
            },
        }
        self._write_json_file(self.project_dir / ".id8/install-manifest.json", payload)

    def _write_env_example(self) -> None:
        github_token = self._mcp_secret_env_var("github")
        stitch_api_key = self._mcp_secret_env_var("stitch")
        vercel_token = self._mcp_secret_env_var("vercel")
        supabase_token = self._mcp_secret_env_var("supabase")
        lines = [
            "# id8 installer generated environment template",
            "# Set these in your shell or copy into your project's .env file.",
            "",
            "# Installer behavior",
            f"ID8_VERCEL_AUTH_MODE={self.vercel_auth_mode}",
            f"ID8_SUPABASE_AUTH_MODE={self.supabase_auth_mode}",
            "ID8_APPEND_ANTIGRAVITY_GLOBAL_MCP=false",
            "",
            "# MCP credentials",
            "# Required",
            f"{github_token}=",
            f"{stitch_api_key}=",
            "",
            "# Required only when *_AUTH_MODE=key",
            f"{vercel_token}=",
            f"{supabase_token}=",
            "",
        ]
        self._write_text_file(self.project_dir / ".env.example", "\n".join(lines))

    def _write_gitignore(self) -> None:
        gitignore_entries = [
            ".env",
            ".mcp.json",
            ".codex/config.toml",
        ]
        lines = [
            GITIGNORE_MARKER_START,
            "# id8 sensitive local files",
            *gitignore_entries,
            GITIGNORE_MARKER_END,
            "",
        ]
        block = "\n".join(lines)
        path = self.project_dir / ".gitignore"
        existing = path.read_text() if path.exists() else ""
        updated = upsert_managed_block(
            existing,
            block,
            marker_start=GITIGNORE_MARKER_START,
            marker_end=GITIGNORE_MARKER_END,
        )
        self._write_text_file(path, updated)

    def _write_json_mcp(
        self,
        path: Path,
        entries: dict[str, dict[str, Any]],
        *,
        url_key: str = "url",
    ) -> None:
        data = self._load_json(path)
        servers = data.get("mcpServers")
        if not isinstance(servers, dict):
            servers = {}
        legacy_keys = [key for key in servers if key.startswith("id8_")]
        for key in legacy_keys:
            servers.pop(key, None)
        for name, server in entries.items():
            normalized = dict(server)
            if url_key != "url" and "url" in normalized:
                normalized[url_key] = normalized.pop("url")
            servers[name] = normalized
        data["mcpServers"] = servers
        self._write_json_file(path, data)

    def _write_toml_block(self, path: Path, block: str) -> None:
        existing = path.read_text() if path.exists() else ""
        updated = upsert_managed_block(existing, block)
        self._write_text_file(path, updated)

    def _write_json_file(self, path: Path, data: dict[str, Any]) -> None:
        text = json.dumps(data, indent=2, sort_keys=True) + "\n"
        self._write_text_file(path, text)

    def _write_text_file(self, path: Path, content: str) -> None:
        if path.exists() and path.read_text() == content:
            return

        if self.args.validate_only:
            self.info.append(f"[validate-only] Would write {path}")
            return

        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            backup = path.with_name(path.name + f".bak.{self._timestamp()}")
            shutil.copy2(path, backup)
            self.backup_files.append(backup)

        path.write_text(content)
        self.changed_files.append(path)

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            loaded = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON file: {path}") from exc
        if not isinstance(loaded, dict):
            raise ValueError(f"Expected JSON object at {path}")
        return loaded

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    def _load_text(self, relative_path: str) -> str:
        target = self.script_dir / relative_path
        if not target.exists():
            raise FileNotFoundError(f"Missing template file: {target}")
        return target.read_text()

    def _render_template(self, relative_path: str, values: dict[str, str]) -> str:
        content = self._load_text(relative_path)
        for key, value in values.items():
            content = content.replace("{{" + key + "}}", value)
        return content

    def _ask_choice(self, label: str, options: tuple[str, ...], default: str) -> str:
        rendered = "/".join(options)
        prompt = f"{label} ({rendered}) [{default}]: "
        while True:
            entered = input(prompt).strip().lower()
            if not entered:
                return default
            if entered in options:
                return entered
            print(f"Invalid choice. Expected one of: {', '.join(options)}")

    def _ask_yes_no(self, question: str, default: bool) -> bool:
        default_str = "Y/n" if default else "y/N"
        prompt = f"{question} [{default_str}]: "
        while True:
            entered = input(prompt).strip().lower()
            if not entered:
                return default
            if entered in {"y", "yes"}:
                return True
            if entered in {"n", "no"}:
                return False
            print("Please answer yes or no.")

    def _print_report(self) -> None:
        mode = "validate-only" if self.args.validate_only else "apply"
        print("\n/id8 installer report")
        print(f"- Mode: {mode}")
        print(f"- Project: {self.project_dir}")
        print(f"- Agents: {', '.join(self.agents)}")
        print(
            "- Antigravity global MCP append: "
            + ("enabled" if self.antigravity_global_append else "disabled")
        )
        print(f"- Vercel auth mode: {self.vercel_auth_mode}")
        print(f"- Supabase auth mode: {self.supabase_auth_mode}")

        if self.changed_files:
            print("- Files written:")
            for path in self.changed_files:
                print(f"  - {path}")
        if self.backup_files:
            print("- Backups created:")
            for path in self.backup_files:
                print(f"  - {path}")
        if self.info:
            print("- Info:")
            for item in self.info:
                print(f"  - {item}")
        if self.pending_auth:
            print("- Pending auth:")
            for item in sorted(self.pending_auth):
                print(f"  - {item}")
        if self.manual_setup:
            print("- Manual setup:")
            for item in self.manual_setup:
                print(f"  - {item}")
        if self.warnings:
            print("- Warnings:")
            for item in self.warnings:
                print(f"  - {item}")

        print("- Invocation examples:")
        if "claude" in self.agents:
            print("  - Claude: /id8")
            print("  - Claude dry-run: /id8 --dry-run")
        if "codex" in self.agents:
            print("  - Codex: $id8")
            print("  - Codex dry-run: $id8 --dry-run")
        if "antigravity" in self.agents:
            print("  - Antigravity: /id8")
            print("  - Antigravity dry-run: /id8 --dry-run")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install project-scoped /id8 workflow assets for selected agents."
    )
    parser.add_argument(
        "--project-dir",
        help="Target project directory. Required in non-interactive mode.",
    )
    parser.add_argument(
        "--agents",
        help="Comma-separated agent list: claude,codex,antigravity. Required in non-interactive mode.",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Disable prompts; auth modes are taken from flags/env or default to oauth.",
    )
    parser.add_argument(
        "--vercel-auth",
        choices=VALID_AUTH_MODES,
        help="Vercel MCP auth mode: oauth or key.",
    )
    parser.add_argument(
        "--supabase-auth",
        choices=VALID_AUTH_MODES,
        help="Supabase MCP auth mode: oauth or key.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow creating the project directory if it does not exist.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate and report changes without writing files.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        installer = Installer(args)
        return installer.run()
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())

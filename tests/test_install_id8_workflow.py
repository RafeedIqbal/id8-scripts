import argparse
import json
import tempfile
import unittest
from pathlib import Path

from install_id8_workflow import (
    MARKER_END,
    MARKER_START,
    Installer,
    build_codex_toml_block,
    parse_agents,
    upsert_managed_block,
)


class InstallWorkflowTests(unittest.TestCase):
    def _make_args(
        self,
        *,
        project_dir: str,
        agents: str = "codex",
        non_interactive: bool = True,
        vercel_auth: str = "oauth",
        supabase_auth: str = "oauth",
        force: bool = False,
        validate_only: bool = True,
    ) -> argparse.Namespace:
        return argparse.Namespace(
            project_dir=project_dir,
            agents=agents,
            non_interactive=non_interactive,
            vercel_auth=vercel_auth,
            supabase_auth=supabase_auth,
            force=force,
            validate_only=validate_only,
        )

    def _manifest_servers(self) -> dict[str, dict[str, str]]:
        manifest = json.loads(Path("assets/id8/mcp_manifest.json").read_text())
        return manifest["servers"]

    def _expected_header(self, server: dict[str, str]) -> str:
        value = f"${{{server['secret_env_var']}}}"
        if server["header_key"].lower() == "authorization":
            value = f"Bearer {value}"
        return f"{server['header_key']}: {value}"

    def _expected_header_dict(self, server: dict[str, str]) -> dict[str, str]:
        value = f"${{{server['secret_env_var']}}}"
        if server["header_key"].lower() == "authorization":
            value = f"Bearer {value}"
        return {server["header_key"]: value}

    def test_parse_agents_deduplicates(self) -> None:
        self.assertEqual(
            parse_agents("claude,codex,claude,antigravity"),
            ["claude", "codex", "antigravity"],
        )

    def test_parse_agents_rejects_invalid(self) -> None:
        with self.assertRaises(ValueError):
            parse_agents("claude,unknown")

    def test_upsert_managed_block_inserts_when_missing(self) -> None:
        original = "model = \"gpt-5\"\n"
        block = f"{MARKER_START}\n[mcp_servers.id8_context7]\nurl = \"x\"\n{MARKER_END}\n"
        updated = upsert_managed_block(original, block)
        self.assertIn(MARKER_START, updated)
        self.assertIn(MARKER_END, updated)

    def test_upsert_managed_block_replaces_existing(self) -> None:
        old_block = f"{MARKER_START}\nold\n{MARKER_END}\n"
        original = f"before\n{old_block}after\n"
        new_block = f"{MARKER_START}\nnew\n{MARKER_END}\n"
        updated = upsert_managed_block(original, new_block)
        self.assertIn("new", updated)
        self.assertNotIn("old", updated)
        self.assertEqual(updated.count(MARKER_START), 1)

    def test_build_codex_toml_block_contains_headers(self) -> None:
        block = build_codex_toml_block(
            {
                "github_mcp_server": {
                    "command": "npx",
                    "args": ["-y", "mcp-remote", "https://example.com"],
                    "enabled": True,
                    "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "abc"},
                }
            }
        )
        self.assertIn("[mcp_servers.github_mcp_server]", block)
        self.assertIn("command =", block)
        self.assertIn("[mcp_servers.github_mcp_server.env]", block)

    def test_codex_entries_are_non_docker_and_use_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = self._make_args(
                project_dir=tmp,
                agents="codex",
                vercel_auth="key",
                supabase_auth="oauth",
                validate_only=True,
            )
            installer = Installer(args)
            entries = installer._build_codex_mcp_entries()

        self.assertNotIn("MCP_DOCKER", entries)
        for config in entries.values():
            self.assertNotEqual(config["command"], "docker")

        context7 = entries["context7"]
        self.assertEqual(
            context7["args"],
            ["-y", "mcp-remote", "https://mcp.context7.com/mcp/oauth"],
        )
        self.assertNotIn("env", context7)

        stitch_args = entries["StitchMCP"]["args"]
        self.assertIn("--header", stitch_args)
        self.assertIn("X-Goog-Api-Key: ${ID8_STITCH_API_KEY}", stitch_args)

        github_args = entries["github_mcp_server"]["args"]
        self.assertIn("Authorization: Bearer ${ID8_GITHUB_TOKEN}", github_args)

        vercel_args = entries["VercelMCP"]["args"]
        self.assertIn("Authorization: Bearer ${ID8_VERCEL_TOKEN}", vercel_args)

        supabase_args = entries["supabase_mcp_server"]["args"]
        joined_supabase = " ".join(supabase_args)
        self.assertNotIn("Authorization: Bearer ${ID8_SUPABASE_TOKEN}", joined_supabase)

    def test_write_env_example_includes_auth_and_key_vars(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = self._make_args(
                project_dir=tmp,
                agents="codex",
                vercel_auth="key",
                supabase_auth="oauth",
                validate_only=False,
            )
            installer = Installer(args)
            installer._write_env_example()
            content = Path(tmp, ".env.example").read_text()

        manifest = self._manifest_servers()
        self.assertIn("ID8_VERCEL_AUTH_MODE=key", content)
        self.assertIn("ID8_SUPABASE_AUTH_MODE=oauth", content)
        self.assertIn(f"{manifest['github']['secret_env_var']}=", content)
        self.assertIn(f"{manifest['stitch']['secret_env_var']}=", content)
        self.assertIn(f"{manifest['vercel']['secret_env_var']}=", content)
        self.assertIn(f"{manifest['supabase']['secret_env_var']}=", content)

    def test_validate_only_missing_dir_does_not_create_and_reports_preview(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp, "new-project")
            args = self._make_args(
                project_dir=str(target),
                agents="codex",
                force=True,
                validate_only=True,
            )
            installer = Installer(args)

        self.assertFalse(target.exists())
        self.assertIn(
            f"[validate-only] Would create project directory: {target.resolve()}",
            installer.info,
        )

    def test_confirmation_gates_match_workflow_deploy_order(self) -> None:
        content = Path("assets/id8/templates/common/confirmation_gates.md").read_text()

        self.assertIn(
            "Before Step 8, ask for explicit approval to provision/deploy backend on Supabase.",
            content,
        )
        self.assertIn(
            "Before Step 9, ask for explicit approval to deploy frontend to Vercel.",
            content,
        )

    def test_design_step_includes_model_choice_and_stitch_export_handoff(self) -> None:
        content = Path("assets/id8/workflow/id8_steps.md").read_text()

        self.assertIn("Gemini 3 flash", content)
        self.assertIn("Gemini 3 pro", content)
        self.assertIn("https://stitch.withgoogle.com/projects/projectID", content)
        self.assertIn("export the screens they like to MCP", content)
        self.assertIn("paste the exported code in the chat", content)

    def test_mcp_entries_follow_manifest_urls_and_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            args = self._make_args(
                project_dir=tmp,
                agents="claude,codex,antigravity",
                vercel_auth="key",
                supabase_auth="key",
                validate_only=True,
            )
            installer = Installer(args)

        manifest = self._manifest_servers()
        expected_stitch_header = self._expected_header(manifest["stitch"])
        expected_github_header = self._expected_header(manifest["github"])
        expected_vercel_header = self._expected_header(manifest["vercel"])
        expected_supabase_header = self._expected_header(manifest["supabase"])

        claude = installer._build_claude_mcp_entries()
        self.assertEqual(claude["context7"]["url"], manifest["context7"]["url"])
        self.assertEqual(claude["stitch"]["url"], manifest["stitch"]["url"])
        self.assertEqual(claude["github"]["url"], manifest["github"]["url"])
        self.assertEqual(claude["vercel"]["url"], manifest["vercel"]["url"])
        self.assertEqual(claude["supabase"]["url"], manifest["supabase"]["url"])
        self.assertEqual(claude["stitch"]["headers"], self._expected_header_dict(manifest["stitch"]))
        self.assertEqual(claude["github"]["headers"], self._expected_header_dict(manifest["github"]))
        self.assertEqual(claude["vercel"]["headers"], self._expected_header_dict(manifest["vercel"]))
        self.assertEqual(claude["supabase"]["headers"], self._expected_header_dict(manifest["supabase"]))

        codex = installer._build_codex_mcp_entries()
        self.assertEqual(codex["context7"]["args"][:3], ["-y", "mcp-remote", manifest["context7"]["url"]])
        self.assertEqual(codex["StitchMCP"]["args"][:3], ["-y", "mcp-remote", manifest["stitch"]["url"]])
        self.assertEqual(codex["github_mcp_server"]["args"][:3], ["-y", "mcp-remote", manifest["github"]["url"]])
        self.assertEqual(codex["VercelMCP"]["args"][:3], ["-y", "mcp-remote", manifest["vercel"]["url"]])
        self.assertEqual(
            codex["supabase_mcp_server"]["args"][:3],
            ["-y", "mcp-remote", manifest["supabase"]["url"]],
        )
        self.assertIn(expected_stitch_header, codex["StitchMCP"]["args"])
        self.assertIn(expected_github_header, codex["github_mcp_server"]["args"])
        self.assertIn(expected_vercel_header, codex["VercelMCP"]["args"])
        self.assertIn(expected_supabase_header, codex["supabase_mcp_server"]["args"])

        antigravity = installer._build_antigravity_mcp_entries()
        self.assertEqual(antigravity["context7"]["serverUrl"], manifest["context7"]["url"])
        self.assertEqual(
            antigravity["StitchMCP"]["args"][:3],
            ["-y", "mcp-remote", manifest["stitch"]["url"]],
        )
        self.assertEqual(
            antigravity["github-mcp-server"]["args"][:3],
            ["-y", "mcp-remote", manifest["github"]["url"]],
        )
        self.assertEqual(
            antigravity["VercelMCP"]["args"][:3],
            ["-y", "mcp-remote", manifest["vercel"]["url"]],
        )
        self.assertEqual(
            antigravity["supabase-mcp-server"]["args"][:3],
            ["-y", "mcp-remote", manifest["supabase"]["url"]],
        )
        self.assertIn(expected_stitch_header, antigravity["StitchMCP"]["args"])
        self.assertIn(expected_github_header, antigravity["github-mcp-server"]["args"])
        self.assertIn(expected_vercel_header, antigravity["VercelMCP"]["args"])
        self.assertIn(expected_supabase_header, antigravity["supabase-mcp-server"]["args"])


if __name__ == "__main__":
    unittest.main()

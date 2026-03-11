# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

id8 (ideate) is an installer that provisions a multi-agent workflow (`/id8`) into target project directories. The workflow turns a prompt into a deployed Next.js app on Vercel through a 9-step pipeline using MCP servers (Context7, Stitch, GitHub, Vercel). It supports three AI agents: Claude Code, Codex, and Antigravity.

## Commands

**Run the installer (interactive):**
```bash
python3 src/install_id8_workflow.py
```

**Run non-interactive:**
```bash
python3 src/install_id8_workflow.py --non-interactive --project-dir ~/my-app --agents claude,codex --vercel-auth oauth
```

**Dry-run (preview without writing):**
```bash
python3 src/install_id8_workflow.py --validate-only
```

**Run tests:**
```bash
cd src && python3 -m unittest discover -s tests -p "test_*.py"
```

## Architecture

The entire installer is a single Python file: `src/install_id8_workflow.py`. It contains:

- **`Installer` class** — the core orchestrator. Resolves config (project dir, agents, auth modes) via CLI args, env vars, or interactive prompts, then writes agent-specific assets into the target project.
- **`upsert_managed_block()`** — idempotent text insertion using marker comments (`# >>> id8-managed:start` / `# <<< id8-managed:end`). Used for `.gitignore` and Codex TOML config so re-runs update rather than duplicate.
- **`build_codex_toml_block()`** — generates TOML MCP server config blocks for Codex's `.codex/config.toml`.

### Key data flow

1. `_load_mcp_servers()` reads `src/assets/id8/mcp_manifest.json` for server URLs and auth metadata.
2. `_template_substitutions()` loads workflow steps and common partials (confirmation gates, dry-run checks).
3. `_render_template()` does `{{KEY}}` substitution into agent-specific `.tmpl` files.
4. Per-agent `_build_*_mcp_entries()` methods produce MCP config in the format each agent expects (JSON for Claude, TOML for Codex, Antigravity-specific JSON).
5. `_write_assets()` writes everything: skills/workflows, MCP configs, `.env.example`, `.gitignore`, and an install manifest.

### Asset structure under `src/assets/id8/`

- `mcp_manifest.json` — single source of truth for MCP server URLs and auth keys
- `workflow/id8_steps.md` — the 9-step workflow definition (shared across all agents)
- `templates/common/` — shared partials (confirmation gates, dry-run checks)
- `templates/{claude,codex,antigravity}/` — agent-specific skill/workflow templates using `{{PLACEHOLDER}}` syntax

### What gets written to the target project

Files vary by selected agents. Claude gets `.claude/skills/id8/SKILL.md` + `.mcp.json`. Codex gets `.agents/skills/id8/SKILL.md` + `.codex/config.toml`. Antigravity gets `.agent/workflows/id8.md` + `.agent/rules/id8.md`. All agents get `.env.example`, `.gitignore` updates, and `.id8/install-manifest.json`.

## Conventions

- All file writes go through `_write_text_file()` which handles backup creation (`.bak.*` suffix) and validate-only mode.
- Managed blocks use marker comments for idempotent updates — never break these markers.
- MCP server names in output configs are not prefixed (e.g., `context7`, not `id8_context7`). The `id8_name` field in the manifest is legacy.
- Vercel auth has two modes: `oauth` (default, no token needed in config) and `key` (requires `ID8_VERCEL_TOKEN`).
- The installer scaffolds a Next.js app via `npx create-next-app@latest id8-src --yes` in the target project directory.

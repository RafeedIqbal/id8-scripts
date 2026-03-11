# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

id8 (ideate) is a multi-agent installer that provisions the `/id8` workflow into target projects. It configures Claude Code, Codex, or Antigravity agents with a 9-step pipeline (PRD → tech plan → design → scaffold → implement → test → git → deploy) to build and deploy Next.js apps on Vercel from a single prompt.

## Commands

```bash
# Run the installer
python3 src/install_id8_workflow.py --project-dir <path> --agents claude,codex,antigravity

# Run tests
cd src && python3 -m unittest discover -s tests -p "test_*.py"

# Run a single test
cd src && python3 -m unittest tests.test_install_id8_workflow.TestInstallerClass.test_parse_agents_deduplicates

# Validate without writing files
python3 src/install_id8_workflow.py --project-dir <path> --validate-only
```

## Architecture

**Single-file installer**: `src/install_id8_workflow.py` is the entire tool. No external Python dependencies — uses only stdlib (argparse, json, pathlib, subprocess, re, shutil).

**Key components inside the installer:**

- **`Installer` class**: Orchestrates scaffolding → asset rendering → config writing → reporting
- **`upsert_managed_block()`**: Inserts/replaces text between `# >>> id8-managed:start` / `# <<< id8-managed:end` markers. This is how `.gitignore` and `.codex/config.toml` are safely updated on re-runs without clobbering user content.
- **`build_codex_toml_block()`**: Generates TOML `[mcp_servers.*]` config for Codex
- **Template rendering**: Substitutes `{{INVOCATION}}`, `{{WORKFLOW_STEPS}}`, `{{DRY_RUN_CHECKS}}`, `{{CONFIRMATION_GATES}}` into agent-specific skill templates

**MCP configuration per agent:**
- Claude Code → HTTP-based entries in `.mcp.json`
- Codex → TOML entries in `.codex/config.toml` using `npx mcp-remote`
- Antigravity → Google Cascade plugin format, optionally global `~/.gemini/antigravity/mcp_config.json`

**4 MCP servers** are defined in `src/assets/id8/mcp_manifest.json`: Context7, Stitch (UI design), GitHub, Vercel. Auth mode (OAuth vs API key) is configurable via `--vercel-auth` flag.

## Key Files

| File | Purpose |
|------|---------|
| `src/install_id8_workflow.py` | Main installer — all logic lives here |
| `src/assets/id8/mcp_manifest.json` | MCP server URLs, auth modes, secret env vars |
| `src/assets/id8/workflow/id8_steps.md` | 9-step workflow definition with technical guardrails |
| `src/assets/id8/templates/` | Agent-specific skill templates (claude/, codex/, antigravity/) |
| `src/assets/id8/templates/common/` | Shared content: confirmation gates, dry-run checks |
| `src/tests/test_install_id8_workflow.py` | Unit tests covering managed blocks, MCP configs, templates |
| `issues.md` | Known deployment edge cases and solutions |

## Design Principles

- **Idempotent**: Safe to re-run. Managed block markers prevent merge conflicts. Files are only written if content actually changed. Existing files are backed up with timestamps.
- **No external deps**: Python stdlib only. Cross-platform launchers (`install.command`, `install.bat`, `install.sh`).
- **Manifest-driven**: MCP URLs and auth are defined in JSON, not hardcoded in installer logic.

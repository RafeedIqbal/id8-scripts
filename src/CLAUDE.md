# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Does

Single-file Python installer (`install_id8_workflow.py`) that writes `/id8` workflow assets into target projects for Claude, Codex, and Antigravity agents. It is not installed itself — it is run from a clone of this repo.

## Commands

```bash
# Interactive install
python3 install_id8_workflow.py

# Non-interactive (CI-safe)
python3 install_id8_workflow.py --non-interactive --project-dir /path/to/project --agents claude,codex,antigravity

# Preview without writing files
python3 install_id8_workflow.py --validate-only --project-dir /path/to/project --agents claude

# Run all tests
python3 -m unittest discover -s tests -p "test_*.py"

# Run a single test method
python3 -m unittest tests.test_install_id8_workflow.TestClassName.test_method_name
```

## Architecture

Everything lives in `install_id8_workflow.py`. Key structure:

- **`Installer` class** — orchestrates the full install: resolves args/env, calls `_write_assets()`, prints a report.
- **`_write_assets()`** — per-agent dispatch: renders templates, calls write helpers (`_write_text_file`, `_write_json_mcp`, `_write_toml_block`).
- **`_template_substitutions()`** — loads `assets/id8/workflow/id8_steps.md` and common partials as template variables.
- **`_load_mcp_servers()`** — reads `assets/id8/mcp_manifest.json` at startup; used by all MCP config builders.
- **`upsert_managed_block()`** — idempotent block insertion/replacement using `# >>> id8-managed:start` / `# <<< id8-managed:end` markers (separate variant for `.gitignore`).

Asset files (templates, workflow steps, MCP manifest) live under `assets/id8/` relative to the script. Templates use `{{PLACEHOLDER}}` syntax. MCP env placeholders use `${ID8_*}` syntax.

Files written to target projects per agent:

| Agent | Files written |
|-------|--------------|
| claude | `.claude/skills/id8/SKILL.md`, `.mcp.json` |
| codex | `.agents/skills/id8/SKILL.md`, `.codex/config.toml` (managed block) |
| antigravity | `.agent/workflows/id8.md`, `.agent/rules/id8.md` |
| all | `.env.example`, `.gitignore` (managed block), `.id8/install-manifest.json` |

## Coding Conventions

- Python 3.9+, 4-space indent, `snake_case` functions/variables, `UPPER_CASE` constants
- Use `pathlib.Path` for all filesystem paths
- Side effects (file writes, subprocess calls) belong inside `Installer` methods only
- Tests use `unittest` with `tempfile.TemporaryDirectory()` for filesystem assertions

## Reference Docs

- `Docs/Agent_Docs/` — per-agent usage notes (ClaudeCode.MD, Codex.MD, Antigravity.MD)
- `Docs/MCP_Docs/` — per-server MCP setup (context7, GitHub, Stitch, Vercel, Supabase)
- `testdir/` — local scratch directory for manual install smoke tests (not tracked output)

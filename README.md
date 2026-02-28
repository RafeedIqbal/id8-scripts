# id8-scripts

Project-only installer for `/id8` workflow assets across Claude, Codex, and Antigravity.

## Requirements

- `python3` (3.9+ recommended)
- Optional CLIs (installer can still write files without them):
  - `claude` for Claude usage
  - `codex` for Codex usage
  - `npm` only if you want installer-assisted CLI install prompts

## Quick Start (Interactive)

The easiest way to run the installer is by running the executable script for your platform from the root of this repository:

- **Windows**: Double-click `install.bat`
- **macOS**: Double-click `install.command`
- **Linux**: Run `./install.sh`

Alternatively, you can run the Python script directly:

```bash
python3 src/install_id8_workflow.py
```

Interactive mode will prompt you for:

1. Project directory
2. Agents (`claude`, `codex`, `antigravity`)
3. Vercel auth mode (`oauth` or `key`)
4. Supabase auth mode (`oauth` or `key`)
5. If `antigravity` is selected: whether to append MCP entries to global Antigravity config

## Non-Interactive Mode

Use this in scripts/CI when you want predictable behavior:

```bash
python3 src/install_id8_workflow.py \
  --non-interactive \
  --project-dir /path/to/project \
  --agents claude,codex,antigravity
```

In non-interactive mode:

- `--project-dir` is required
- `--agents` is required
- Vercel/Supabase auth mode defaults to `oauth` unless set via flags/env
- Antigravity global MCP append defaults to `false` unless overridden

## Validate-Only (Dry Install Preview)

```bash
python3 src/install_id8_workflow.py \
  --validate-only \
  --project-dir /path/to/project \
  --agents claude,codex,antigravity
```

This shows what would be written without modifying files.

## CLI Options

```bash
python3 src/install_id8_workflow.py --help
```

Supported flags:

- `--project-dir <path>`: target project directory (required in non-interactive mode)
- `--agents claude,codex,antigravity`: comma-separated selected agents (required in non-interactive mode)
- `--non-interactive`: disables prompts
- `--vercel-auth oauth|key`: set Vercel MCP auth mode
- `--supabase-auth oauth|key`: set Supabase MCP auth mode
- `--force`: create missing project directory automatically
- `--validate-only`: preview changes only

## Environment Variables

Auth mode overrides for non-interactive installs:

- `ID8_VERCEL_AUTH_MODE=oauth|key`
- `ID8_SUPABASE_AUTH_MODE=oauth|key`

MCP templates include placeholders for these key variables:

- `ID8_GITHUB_TOKEN`
- `ID8_VERCEL_TOKEN`
- `ID8_SUPABASE_TOKEN`
- `ID8_STITCH_API_KEY`

Antigravity global MCP append toggle:

- `ID8_APPEND_ANTIGRAVITY_GLOBAL_MCP=true|false`

## What Gets Installed

Project-scoped files:

- Claude skill: `.claude/skills/id8/SKILL.md`
- Claude MCP config: `.mcp.json`
- Codex skill: `.agents/skills/id8/SKILL.md`
- Codex MCP config: `.codex/config.toml`
- Antigravity workflow: `.agent/workflows/id8.md`
- Antigravity rule: `.agent/rules/id8.md`
- Project `.gitignore` block for sensitive local files (`.env`, `.mcp.json`, `.codex/config.toml`)
- Environment template: `.env.example`
- Installer manifest: `.id8/install-manifest.json`

Optional global file (only if confirmed for Antigravity):

- `~/.gemini/antigravity/mcp_config.json`

## MCP Key Configuration

Generated MCP configs use OAuth for Context7 and env-var placeholders for key-based servers (for example `${ID8_STITCH_API_KEY}` and `${ID8_GITHUB_TOKEN}`).

You can configure keys in one of two ways:

1. Set environment variables before launching your MCP client (the installer writes starter values in `.env.example`).
2. Replace placeholder values directly in the MCP config files:
   - Project Claude MCP: `.mcp.json`
   - Project Codex MCP block: `.codex/config.toml`
   - Global Antigravity MCP config (if enabled): `~/.gemini/antigravity/mcp_config.json`

The installer also writes a managed `.gitignore` block covering `.env`, `.mcp.json`, and `.codex/config.toml`.
If you put real keys directly in any other project files, add those files to `.gitignore` as well.

## Invocation After Install

- Claude: `/id8` and `/id8 --dry-run`
- Codex: `$id8` and `$id8 --dry-run`
- Antigravity: `/id8` and `/id8 --dry-run`

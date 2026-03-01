# id8

**From prompt to deployed product in one conversation.**

id8 (ideate) is a multi-agent workflow that turns a single idea into a fully deployed full-stack application — complete with AI-generated designs, a Next.js frontend on Vercel, and a Supabase backend — all orchestrated through your AI coding agent of choice.

This repository is the installer. Run it against any project directory to provision the `/id8` workflow for **Claude Code**, **Codex**, or **Antigravity**.

---

## How It Works

id8 orchestrates a 10-step pipeline with confirmation gates at every critical juncture:

| Step | What happens | Tools used |
|------|-------------|------------|
| **1. PRD** | Generates a structured product requirements doc from your prompt | Agent |
| **2. Tech Plan** | Creates an implementation plan scoped to Vercel + Supabase | Context7 MCP |
| **3. Design** | Produces UI screens via AI (optional) | Stitch MCP |
| **4. Scaffold** | Sets up Next.js frontend + Supabase backend structure | Agent |
| **5. Implement** | Writes full-stack code from screens, PRD, and tech plan | Agent + Context7 |
| **6. Test** | Runs dev and production builds locally, fixes issues | Agent |
| **7. Git** | Creates repo, runs secret scan, pushes code | GitHub MCP |
| **8. Backend** | Deploys Supabase project, applies migrations, enables RLS | Supabase MCP |
| **9. Frontend** | Deploys to Vercel, wires environment variables | Vercel MCP/CLI |
| **10. Verify** | Smoke-tests live deployment, publishes completion report | Agent |

Steps 7-9 require explicit user confirmation before executing.

---

## Quick Start

### 1. Clone this repo

```bash
git clone https://github.com/rafeediqbal/id8-scripts.git
cd id8-scripts
```

### 2. Run the installer

**macOS** — double-click `install.command` or:
```bash
python3 src/install_id8_workflow.py
```

**Windows** — double-click `install.bat`

**Linux** — run `./install.sh`

The interactive installer will ask for:
1. Target project directory
2. Which agents to configure (`claude`, `codex`, `antigravity`)
3. Auth mode for Vercel and Supabase (`oauth` or `key`)

### 3. Set up your API keys

Copy the generated `.env.example` to `.env` in your project and fill in your keys:

```
ID8_GITHUB_TOKEN=ghp_...
ID8_STITCH_API_KEY=...
ID8_VERCEL_TOKEN=...        # only if using key-based auth
ID8_SUPABASE_TOKEN=...      # only if using key-based auth
```

### 4. Launch the workflow

Open your project in your agent and invoke:

| Agent | Command |
|-------|---------|
| Claude Code | `/id8` |
| Codex | `$id8` |
| Antigravity | `/id8` |

Append `--dry-run` to test MCP connectivity without building anything.

---

## CLI Reference

```
python3 src/install_id8_workflow.py [OPTIONS]
```

| Flag | Description |
|------|-------------|
| `--project-dir <path>` | Target project directory |
| `--agents <list>` | Comma-separated: `claude`, `codex`, `antigravity` |
| `--non-interactive` | No prompts — suitable for CI |
| `--vercel-auth oauth\|key` | Vercel MCP auth mode |
| `--supabase-auth oauth\|key` | Supabase MCP auth mode |
| `--force` | Create project directory if it doesn't exist |
| `--validate-only` | Preview what would be written without modifying files |

### Non-interactive example

```bash
python3 src/install_id8_workflow.py \
  --non-interactive \
  --project-dir ~/projects/my-app \
  --agents claude,codex \
  --vercel-auth oauth \
  --supabase-auth oauth
```

### Environment variable overrides

| Variable | Purpose |
|----------|---------|
| `ID8_VERCEL_AUTH_MODE` | Override Vercel auth mode (`oauth` or `key`) |
| `ID8_SUPABASE_AUTH_MODE` | Override Supabase auth mode (`oauth` or `key`) |
| `ID8_APPEND_ANTIGRAVITY_GLOBAL_MCP` | Auto-append global MCP config for Antigravity (`true`/`false`) |

---

## What Gets Installed

The installer writes the following into your target project:

```
your-project/
  .claude/skills/id8/SKILL.md      # Claude workflow skill
  .agents/skills/id8/SKILL.md      # Codex workflow skill
  .agent/workflows/id8.md           # Antigravity workflow
  .agent/rules/id8.md               # Antigravity rules
  .mcp.json                         # Claude MCP server config
  .codex/config.toml                # Codex MCP config (managed block)
  .env.example                      # Environment variable template
  .gitignore                        # Managed block for secrets
  .id8/install-manifest.json        # Installation metadata
```

Only files for selected agents are written. All writes are idempotent — re-running the installer updates existing files safely with automatic backups.

---

## MCP Servers

id8 connects to five MCP servers to power the full workflow:

| Server | Purpose | Auth |
|--------|---------|------|
| **Context7** | Library documentation lookup | OAuth |
| **Stitch** | AI UI design generation | API key |
| **GitHub** | Repository creation and code push | API key |
| **Vercel** | Frontend deployment | OAuth or API key |
| **Supabase** | Backend deployment and database management | OAuth or API key |

Detailed setup guides for each server are in [`src/Docs/MCP_Docs/`](src/Docs/MCP_Docs/).

---

## Requirements

- **Python 3.9+**
- One or more supported AI agents:
  - [`claude`](https://docs.anthropic.com/en/docs/claude-code) — Claude Code CLI
  - [`codex`](https://github.com/openai/codex) — OpenAI Codex CLI
  - Antigravity — Google's Cascade agent
- **npm/npx** — for Next.js scaffolding during the workflow
- **git** — for repository operations

---

## Project Structure

```
id8-scripts/
  src/
    install_id8_workflow.py          # Main installer (single-file)
    assets/id8/
      workflow/id8_steps.md          # 10-step workflow definition
      templates/                     # Agent-specific skill templates
        claude/SKILL.md.tmpl
        codex/SKILL.md.tmpl
        antigravity/id8_workflow.md.tmpl
        antigravity/id8_rule.md.tmpl
        common/                      # Shared partials
      mcp_manifest.json              # MCP server definitions
    tests/
      test_install_id8_workflow.py   # Unit tests
    Docs/
      Agent_Docs/                    # Per-agent setup guides
      MCP_Docs/                      # Per-server MCP guides
  install.bat                        # Windows launcher
  install.command                    # macOS launcher
  install.sh                         # Linux launcher
```

---

## Running Tests

```bash
cd src
python3 -m unittest discover -s tests -p "test_*.py"
```

---

## License

MIT

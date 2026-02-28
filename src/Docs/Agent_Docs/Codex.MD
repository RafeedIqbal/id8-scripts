# Codex Documentation

Codex is a powerful development assistant designed to integrate deeply with your tools, environment, and workflows. This guide covers the core extensibility features: Model Context Protocol (MCP), execution rules, and agent skills.

---

## 📋 Table of Contents

1. [Model Context Protocol (MCP)](#-model-context-protocol-mcp)
   - [Supported Features](#supported-mcp-features)
   - [Connection & Configuration](#connect-codex-to-an-mcp-server)
   - [Configuring via CLI](#configure-with-the-cli)
   - [Configuring via config.toml](#configure-with-configtoml)
2. [Rules](#-rules)
   - [Creating Rules](#create-a-rules-file)
   - [Rule Fields](#understand-rule-fields)
   - [Shell Wrappers & Compounds](#shell-wrappers-and-compound-commands)
   - [Testing Rules](#test-a-rule-file)
3. [Agent Skills](#-agent-skills)
   - [Skill Discovery](#how-codex-uses-skills)
   - [Creating a Skill](#create-a-skill)
   - [Storage Locations](#where-to-save-skills)
   - [Metadata & Best Practices](#optional-metadata)

---

## 🔌 Model Context Protocol (MCP)

The Model Context Protocol (MCP) connects models to real-world tools and context. Use it to give Codex access to third-party documentation, or to let it interact with developer tools like your browser, Figma, or internal databases.

Codex supports MCP servers in both the CLI and the IDE extension.

### Supported MCP Features

- **STDIO Servers**: Servers that run as a local process (started by a command).
  - Full support for environment variables.
- **Streamable HTTP Servers**: Remote servers accessed at a URL.
  - Bearer token authentication.
  - OAuth authentication (run `codex mcp login <server-name>` for supported servers).

### Connect Codex to an MCP Server

Codex stores MCP configuration in `config.toml` alongside other assistant settings. 

| Scope | Configuration Path |
| :--- | :--- |
| **Global** | `~/.codex/config.toml` |
| **Project** | `.codex/config.toml` (Trusted projects only) |

> [!TIP]
> The CLI and the IDE extension share this configuration. Once configured, you can switch between clients without redoing setup.

### Configure with the CLI

#### Add an MCP Server
```bash
codex mcp add <server-name> --env VAR1=VALUE1 --env VAR2=VALUE2 -- <stdio server-command>
```

**Example: Adding Context7** (Developer documentation server):
```bash
codex mcp add context7 -- npx -y @upstash/context7-mcp
```

#### Management Commands
- **View Help**: Run `codex mcp --help`.
- **Active Servers**: In the `codex` TUI, use the `/mcp` command.

### Configure with config.toml

For fine-grained control, edit the configuration file directly. In the IDE, select **MCP settings** > **Open config.toml** from the settings menu. Each server is defined under a `[mcp_servers.<name>]` table.

#### Server Type Options

| Category | Options | Description |
| :--- | :--- | :--- |
| **STDIO** | `command` | The execution command (Required). |
| | `args` | List of arguments to pass. |
| | `env` | Key-value pairs of environment variables. |
| | `cwd` | Working directory for the server process. |
| **HTTP** | `url` | The server endpoint (Required). |
| | `bearer_token_env_var` | Env var name containing the token. |
| | `http_headers` | Static header mapping. |

#### Global Server Settings

- `enabled`: Set to `false` to pause a server.
- `startup_timeout_sec`: Seconds to wait for initialization (Default: `10`).
- `tool_timeout_sec`: Seconds allowed for tool execution (Default: `60`).
- `enabled_tools` / `disabled_tools`: Allow/Deny lists for specific tools.

#### config.toml Examples

```toml
# STDIO Example: Context7
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]
[mcp_servers.context7.env]
MY_ENV_VAR = "MY_ENV_VALUE"

# HTTP Example: Figma
[mcp_servers.figma]
url = "https://mcp.figma.com/mcp"
bearer_token_env_var = "FIGMA_OAUTH_TOKEN"
http_headers = { "X-Figma-Region" = "us-east-1" }
```

---

## 📜 Rules

Rules control which commands Codex can execute outside the sandbox environment. This experimental feature ensures security while maintaining flexibility.

### Create a Rules File

1. Create a `.rules` file in `~/.codex/rules/` (e.g., `default.rules`).
2. Define a rule using the `prefix_rule` syntax:

```python
# Prompt before running 'gh pr view' outside the sandbox.
prefix_rule(
    pattern = ["gh", "pr", "view"],
    decision = "prompt",
    justification = "Viewing PRs is allowed with approval",
    match = [
        "gh pr view 7888",
        "gh pr view --repo openai/codex",
    ],
    not_match = [
        "gh pr --repo openai/codex view 7888", # Pattern must be an exact prefix
    ],
)
```

> [!IMPORTANT]
> Codex scans `rules/` under every Team Config location at startup. When you "Allow" a command in the TUI, it is automatically added to `~/.codex/rules/default.rules`.

### Understand Rule Fields

| Field | Default | Description |
| :--- | :--- | :--- |
| **pattern** | *(Required)* | A list of string literals or unions `["a", "b"]` to match command prefixes. |
| **decision** | `"allow"` | One of: `allow` (run), `prompt` (ask), or `forbidden` (block). |
| **justification**| `""` | Human-readable reason displayed in UI prompts. |
| **match** / **not_match** | `[]` | Unit tests to validate rule logic during load. |

### Shell Wrappers and Compound Commands

Codex handles complex shell strings (e.g., `bash -c "..."`) with intelligent parsing:

> [!NOTE]
> **Safe Splitting**: If a script is a linear chain (using `&&`, `||`, `;`, `|`) without variable expansion or assignments, Codex splits it into individual commands and evaluates each against your rules.

**Advanced Features**: If a script uses redirections (`>`), substitutions (`$(...)`), or wildcard patterns (`*`), Codex treats the **entire** string as a single invocation for increased security.

### Test a Rule File

Use the `execpolicy` tool to verify your rules:

```bash
codex execpolicy check --pretty \
  --rules ~/.codex/rules/default.rules \
  -- gh pr view 7888 --json title,body,comments
```

---

## 🧠 Agent Skills

Skills package instructions, scripts, and resources into reusable workflows. They use **progressive disclosure** to keep the context window lean, loading full instructions only when needed.

### Skill Directory Structure

```text
my-skill/
├── SKILL.md       # Required: Metadata + instructions
├── scripts/       # Optional: Executable code
├── references/    # Optional: External documentation
├── assets/        # Optional: Templates and UI resources
└── agents/        
    └── openai.yaml # Optional: UI branding & dependencies
```

### How Codex Uses Skills

- **Explicit**: Mention a skill using `$` in the input box or run `/skills`.
- **Implicit**: Codex automatically selects a skill if its `description` matches your current task.

> [!TIP]
> Write skill descriptions with clear "boundaries" to help Codex understand exactly when the skill should be activated.

### Create a Skill

1. **Auto-Creator**: Run `$skill-creator` for an interactive setup.
2. **Manual**: Create a folder with a `SKILL.md` file:

```markdown
---
name: skill-name
description: Explain exactly when this skill should and should not trigger.
---

Skill instructions for Codex to follow.
```

### Where to Save Skills

Codex scans for skills in the following order:

| Scope | Path | Best Use |
| :--- | :--- | :--- |
| **REPO** | `.agents/skills` | Project-specific logic (e.g., microservice deploy). |
| **USER** | `~/.agents/skills` | Personal productivity tools and global shortcuts. |
| **ADMIN** | `/etc/codex/skills` | SDKs and company-wide automation defaults. |
| **SYSTEM** | *(Built-in)* | Core skills like `skill-creator` and `plan`. |

### Optional Metadata (openai.yaml)

Configure the UI appearance and declare tool dependencies:

```yaml
interface:
  display_name: "GitHub Manager"
  brand_color: "#3B82F6"
  icon_small: "./assets/icon.svg"

dependencies:
  tools:
    - type: "mcp"
      value: "github-mcp-server"
      description: "GitHub API access"

policy:
  allow_implicit_invocation: true
```

---

## 💡 Best Practices

- **Focused Scope**: Each skill should handle one logical domain.
- **Clear Descriptions**: Use keywords that reflect the agent's likely tasks.
- **Instruction First**: Prefer Markdown instructions over complex scripts unless deterministic behavior is required.
- **Test Often**: Use the TUI to verify that skills trigger correctly for your use cases.
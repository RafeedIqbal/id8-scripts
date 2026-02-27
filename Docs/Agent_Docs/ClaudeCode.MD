# 🛠️ Claude Code: Skills & MCP Integration

> Extend Claude's capabilities with custom skills, slash commands, and Model Context Protocol (MCP) integrations.

Skills and MCP are the two primary ways to broaden Claude Code's horizons. **Skills** allow you to teach Claude new workflows and patterns, while **MCP** connects Claude to external tools, databases, and APIs.

---

## 🧠 Part 1: Agent Skills

Skills extend what Claude can do. By creating a `SKILL.md` file with specific instructions, Claude adds it to its toolkit. Claude uses skills automatically when relevant, or you can invoke them directly via slash commands.

### 🚀 Getting Started

#### 1. Create Your First Skill
This example creates a skill that teaches Claude to explain code using visual diagrams and analogies.

**A. Create the skill directory:**
Personal skills are available across all your projects.
```bash
mkdir -p ~/.claude/skills/explain-code
```

**B. Write `SKILL.md`:**
Every skill needs a `SKILL.md` consisting of YAML frontmatter and Markdown instructions.
```yaml
---
name: explain-code
description: Explains code with visual diagrams and analogies. Use when explaining how code works, teaching about a codebase, or when the user asks "how does this work?"
---

When explaining code, always include:
1. **Analogy**: Compare the code to an everyday concept.
2. **Diagram**: Use ASCII art to show flow or relationships.
3. **Walkthrough**: Explain step-by-step logic.
4. **Gotcha**: Highlight a common pitfall.

Keep explanations conversational and use multiple analogies for complex logic.
```

**C. Test the Skill:**
- **Automatic**: Ask Claude "How does this code work?"
- **Manual**: Use `/explain-code src/auth/login.ts`

---

### 📂 Skill Locations & Priority

Where you store a skill determines its scope and overrides.

| Scope | Path | Target |
| :--- | :--- | :--- |
| **Enterprise** | Managed Settings | Entire Organization |
| **Personal** | `~/.claude/skills/` | All your projects |
| **Project** | `.claude/skills/` | Current project only |
| **Plugin** | `<plugin>/skills/` | Plugin-specific |

> [!IMPORTANT]
> **Precedence:** Enterprise > Personal > Project.
> Conflicts are resolved by choosing the higher-priority location.

---

### ⚙️ Skill Configuration (Frontmatter)

Configure behavior using YAML frontmatter at the top of `SKILL.md`.

| Field | Description | Default |
| :--- | :--- | :--- |
| `name` | The slash command name (e.g., `/my-skill`). | Dir name |
| `description` | Helps Claude decide when to auto-invoke. | First para |
| `argument-hint` | Hint shown in autocomplete (e.g., `[issue-id]`). | None |
| `disable-model-invocation` | If `true`, Claude won't auto-trigger it. | `false` |
| `user-invocable` | If `false`, hidden from the `/` menu. | `true` |
| `allowed-tools` | Tools Claude can use without asking (active skill only). | None |
| `context: fork` | Runs the skill in an isolated subagent context. | `false` |

---

### 🔗 String Substitutions & Dynamic Context

#### Variable Substitutions
Use these placeholders to pass data into your skill prompts:
- `$ARGUMENTS`: All arguments passed.
- `$0`, `$1`, ...: Positional arguments.
- `${CLAUDE_SESSION_ID}`: The current unique session ID.

#### Dynamic Context Injection
Run shell commands before sending the prompt to Claude using the `!command` syntax.
```markdown
## Live PR Context
- PR Diff: !`gh pr diff`
- Comments: !`gh pr view --comments`
```
*Claude receives the processed output of these commands, not the commands themselves.*

---

### 🧪 Advanced Skill Patterns

#### Subagents (`context: fork`)
Use `context: fork` to run skills in isolation. This is perfect for complex research or long-running tasks that shouldn't clutter the main history.

```yaml
---
name: deep-research
description: Thoroughly research a topic
context: fork
agent: Explore
---
Research $ARGUMENTS thoroughly using Glob and Grep...
```

#### Supporting Files
Keep `SKILL.md` under 500 lines. Move large references to separate files within the skill directory.
```text
my-skill/
├── SKILL.md      # Entrypoint & Logic
├── reference.md  # Detailed API docs
└── scripts/      # Helper utilities
```

---

## 🔌 Part 2: Model Context Protocol (MCP)

Claude Code connects to external tools, databases, and APIs through the [Model Context Protocol](https://modelcontextprotocol.io/).

### ⚡ What You Can Do
- **Issue Tracking**: "Add feature X from Jira and create a GitHub PR."
- **Data Analysis**: "Query PostgreSQL for the top 10 users."
- **Designs**: "Update CSS based on the Figma link provided."
- **Automation**: "Draft Gmail invites for the feedback group."

---

### 📥 Installing MCP Servers

#### Option 1: Remote HTTP (Recommended)
```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

#### Option 2: Local Stdio
Stdio servers run as local processes. Use `--` to separate Claude's flags from the command.
```bash
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub --dsn "..."
```

> [!TIP]
> **Scope Your Servers:**
> - `--scope local`: Private to current project.
> - `--scope project`: Shared via `.mcp.json` (commit to Git).
> - `--scope user`: Available across all projects.

---

### 🛡️ Permissions & Security

- **View Status**: Run `/mcp` inside Claude Code.
- **Limit Access**: Use [permission settings](/en/permissions) to allow/deny specific tools.
- **Trust**: Only install MCP servers from sources you trust.

---

### 🏢 Managed MCP (Enterprise)

Administrators can enforce MCP configurations via `managed-mcp.json`.
- **macOS**: `/Library/Application Support/ClaudeCode/managed-mcp.json`
- **Linux**: `/etc/claude-code/managed-mcp.json`

```json
{
  "allowedMcpServers": [
    { "serverName": "github" },
    { "serverUrl": "https://*.internal.corp/*" }
  ]
}
```

---

### 🛠️ Practical MCP Examples

#### 🐞 Debugging with Sentry
1. `claude mcp add --transport http sentry https://mcp.sentry.dev/mcp`
2. Run `/mcp` to authenticate.
3. Ask: *"What are the most common errors in the last 24h?"*

#### 🗄️ Database Queries
1. `claude mcp add --transport stdio db -- npx -y @bytebase/dbhub --dsn "..."`
2. Ask: *"What's our total revenue this month?"*

---

### ❓ Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Skill not triggering** | Check if description matches user keywords or invoke via `/name`. |
| **Too many skills** | Claude may exclude some to save tokens. check `/context` for warnings. |
| **MCP Timeout** | Adjust `MCP_TIMEOUT` environment variable. |
| **Windows npx fix** | Use `cmd /c npx` for local stdio servers. |

---

## 📚 Related Resources
- **[Subagents](/en/sub-agents)**: Delegate tasks.
- **[Plugins](/en/plugins)**: Package skills/MCP together.
- **[Hooks](/en/hooks)**: Automate tool workflows.
- **[Permissions](/en/permissions)**: Control access security.

## 🛠 Rules

Rules are manually defined constraints for the Agent to follow at both local and global levels. They allow you to guide the agent's behavior to match your specific use cases, coding standards, and architectural preferences.

### Getting Started with Rules

1. Open the **Customizations** panel via the `...` dropdown at the top of the editor's agent panel.
2. Navigate to the **Rules** tab.
3. Click `+ Global` for cross-project rules, or `+ Workspace` for project-specific constraints.
4. Input your instructions in the Markdown editor.

> [!NOTE]
> Individual Rules files are limited to 12,000 characters each.

### Global Rules
Global rules are applied across all workspaces and reside in:
`~/.gemini/GEMINI.md`

### Workspace Rules
Workspace-specific rules live in the `.agent/rules` folder of your workspace or Git root.

### Activation Modes

You can define how a rule should be activated:

| Mode | Description |
| :--- | :--- |
| **Manual** | Activated only via `@mention` in the Agent's input box. |
| **Always On** | Rule is always applied to every interaction. |
| **Model Decision** | The model decides based on context whether to apply the rule. |
| **Glob** | Applied automatically to files matching a pattern (e.g., `src/**/*.ts`). |

### @ Mentions
You can reference other files using `@filename` within a Rules file. 
- **Relative paths**: Interpreted relative to the Rules file location.
- **Absolute paths**: Resolved as a true absolute path.
- **Root-relative**: `@/path/to/file.md` will check the absolute path first, then fall back to `workspace/path/to/file.md`.

---

## 🔄 Workflows

Workflows enable you to define a series of steps to guide the Agent through repetitive tasks, such as deploying services or responding to PR comments. These are saved as `.md` files and can be invoked via slash commands (e.g., `/deploy`).

### Creating Workflows

1. Open **Customizations** > **Workflows**.
2. Create a **Global** (system-wide) or **Workspace** (project-specific) workflow.
3. Define the title, description, and sequential steps.

> [!NOTE]
> Workspace-specific workflows live in the `.agent/workflows` folder of your workspace or Git root.

> [!TIP]
> You can call workflows from within other workflows! For example, `/test-suite` could include an instruction to "Call `/lint-check`".

### Agent-Generated Workflows
You can ask the agent to generate a workflow for you! This is highly effective after you have manually completed a series of steps with the agent, as it can use the conversation history to distill the process into a repeatable markdown format.

---

## 🧠 Agent Skills

Skills are an open standard for extending agent capabilities. A skill is a folder containing a `SKILL.md` file with instructions, best practices, and optional resources.

### Skill Locations

| Scope | Location |
| :--- | :--- |
| **Workspace** | `<workspace-root>/.agent/skills/<skill-folder>/` |
| **Global** | `~/.gemini/antigravity/skills/<skill-folder>/` |

### Skill Structure

While only `SKILL.md` is required, a full skill folder might look like this:

```text
.agent/skills/my-skill/
├── SKILL.md       # Main instructions (Required)
├── scripts/       # Helper scripts & CLI utilities (Optional)
├── examples/      # Reference implementations (Optional)
└── resources/     # Templates and other static assets (Optional)
```

### Creating a Skill

Every skill needs a `SKILL.md` with YAML frontmatter:

```markdown
---
name: my-skill
description: Comprehensive description of when the agent should use this skill.
---

# My Skill Name

## Detailed Instructions
Provide step-by-step guidance, conventions, and patterns here.

## When to Use
- Scenario A
- Scenario B
```

> [!IMPORTANT]
> The `description` field is critical. It is what the agent reads when deciding whether to "activate" the skill for the current task.

### Best Practices
- **Keep it Focused**: One skill should solve one logical domain.
- **Clear Descriptions**: Use keywords the agent is likely to recognize.
- **Script Discovery**: If using scripts, instruct the agent to run them with `--help` first to save context window space.

---

## 🔌 MCP Integration

Antigravity supports the **Model Context Protocol (MCP)**, allowing the editor to securely connect to local tools, databases, and external services.

### Core Features

1. **Context Resources**: The AI reads data from connected servers (e.g., live Neon/Supabase schemas, build logs from Vercel).
2. **Custom Tools**: Execute actions defined by servers (e.g., "Create a Linear issue", "Search Notion").

### How to Connect

Connections are managed through the built-in **MCP Store**:
1. Access the **MCP Store** via the `...` dropdown in the agent panel.
2. Browse and **Install** supported servers.
3. Authenticate as prompted to link your accounts.

### Custom MCP Servers

To connect to a private or custom server:
1. Open the MCP Store > **Manage MCP Servers**.
2. Click **View raw config**.
3. Manually modify the `mcp_config.json` with your server configuration.

> [!CAUTION]
> Always verify the source and permissions of custom MCP servers before adding them to your configuration.
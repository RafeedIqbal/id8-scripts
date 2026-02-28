# Vercel via MCP

Connect your AI tools to Vercel using the [Model Context Protocol (MCP)](https://modelcontextprotocol.io), an open standard that lets AI assistants interact with your Vercel projects securely.

---

## What is Vercel MCP?

Vercel MCP is Vercel's official MCP server. It's a remote MCP with OAuth that gives AI tools secure access to your Vercel projects.

**Official Endpoint:** `https://mcp.vercel.com`

It integrates with popular AI assistants like Claude, enabling you to:
- **Search and navigate** Vercel documentation.
- **Manage** projects and deployments.
- **Analyze** deployment logs.

Vercel MCP implements the latest [MCP Authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization) and [Streamable HTTP](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#streamable-http) specifications.

---

## Supported Clients

Currently, the following AI tools can connect to Vercel MCP:

| Category | Supported Clients |
| :--- | :--- |
| **CLIs** | Claude Code, Codex CLI, Gemini CLI |
| **IDEs / Extensions** | Cursor, VS Code (Copilot), Gemini Code Assist, Windsurf |
| **Agentic Platforms** | ChatGPT, Devin, Raycast, Goose |

---

## Setup

Connect your AI client to Vercel MCP and authorize access to manage your Vercel projects.

### Install with `add-mcp`
The simplest way to install the MCP server for all your coding agents:
```bash
npx add-mcp https://mcp.vercel.com
```
The `add-mcp` tool automatically detects your installed AI clients and configures Vercel MCP for each one.
- Add `-y` to skip confirmation.
- Add `-g` to install globally across all projects.

### Claude Code
```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Add Vercel MCP
claude mcp add --transport http vercel https://mcp.vercel.com

# Start coding
claude

# Authenticate the MCP tools
/mcp
```

### Cursor
Add the snippet below to your project-specific or global `.cursor/mcp.json` file.
```json
{
  "mcpServers": {
    "vercel": {
      "url": "https://mcp.vercel.com"
    }
  }
}
```
> [!NOTE]
> Once added, Cursor will display a **"Needs login"** prompt. Click it to authorize access.

### VS Code with Copilot
1. Open the Command Palette (`Cmd+Shift+P` on macOS, `Ctrl+Shift+P` on manual).
2. Run **MCP: Add Server** -> Select **HTTP**.
3. **URL:** `https://mcp.vercel.com` | **Name:** `Vercel`.
4. Run **MCP: List Servers** -> Select **Vercel** -> **Start Server**.
5. When prompted to authenticate, follow the URL Handler flow if the standard browser flow fails.

### ChatGPT
> [!NOTE]
> Custom connectors using MCP are available for **Pro and Plus** accounts on the web.

1. Enable **Developer mode** in Settings → Connectors → Advanced.
2. Under Connectors, click **Create**:
   - **Name:** `Vercel`
   - **MCP server URL:** `https://mcp.vercel.com`
   - **Authentication:** `OAuth`

### Gemini Code Assist & CLI
Add the following to your `~/.gemini/settings.json`:
```json
{
  "mcpServers": {
    "vercel": {
      "command": "npx",
      "args": ["mcp-remote", "https://mcp.vercel.com"]
    }
  }
}
```

---

## Security Best Practices

> [!IMPORTANT]
> **Trust and Verification:** Only use MCP clients from trusted sources. Connecting to Vercel MCP grants the AI system the same access levels as your personal Vercel account.

- **Verify Endpoints:** Always ensure you are connecting to `https://mcp.vercel.com`.
- **Human Confirmation:** Always enable human confirmation in your workflows to maintain control and prevent unauthorized changes.
- **Prompt Injection:** Be aware of [prompt injection](https://vercel.com/blog/building-secure-ai-agents) risks where malicious instructions could attempt to exfiltrate data.
- **Confused Deputy Protection:** Vercel MCP requires explicit user consent for each client connection to prevent exploitation of consent cookies.

---

## Advanced Usage: Project-Specific Access

For enhanced performance, you can use project-specific URLs that provide automatic team and project context:

`https://mcp.vercel.com/<teamSlug>/<projectSlug>`

### Benefits
- **Automatic Context:** The server knows the project/team immediately.
- **Improved Performance:** Tools execute without requiring manual parameter input.
- **Better Error Handling:** Reduces "Missing project slug" errors.

---

## Tool Reference

### Documentation Tools

#### `search_documentation`
Search Vercel documentation for specific topics.
- `topic` (string, Required): The topic (e.g., 'routing', 'data-fetching').
- `tokens` (number): Max tokens (default: 2500).

---

### Project & Team Tools

#### `list_teams`
List all teams where the authenticated user is a member.

#### `list_projects`
List all Vercel projects for a given team.
- `teamId` (string, Required): ID or slug of the team.

#### `get_project`
Get details about a specific project.
- `projectId` (string, Required): ID or slug of the project.
- `teamId` (string, Required): ID or slug of the team.

---

### Deployment Tools

#### `list_deployments`
List deployments for a specific project.
- `projectId`/`teamId` (Required).
- `since`/`until` (Optional): Timestamps for filtering.

#### `get_deployment`
Get detailed info for a specific deployment.
- `idOrUrl` (string, Required): Unique ID or hostname.

#### `get_deployment_build_logs`
Investigate build failures.
- `idOrUrl` (Required).
- `limit` (Default: 100).

#### `get_runtime_logs`
Debug execution errors in Vercel Functions.
- Supports filtering by `level` (`error`, `warning`, `info`), `environment`, `statusCode`, and `source`.

---

### Domain Management

#### `check_domain_availability_and_price`
Check if domains (e.g., `example.com`) are available for purchase.

#### `buy_domain`
Purchase a domain (requires full registrant information).

---

### Utility Tools

#### `get_access_to_vercel_url`
Create a temporary shareable link to bypass authentication for protected deployments.

#### `web_fetch_vercel_url`
Fetch content directly from a deployment (handles Vercel Authentication automatically).

#### `deploy_to_vercel`
Easily deploy the current project directory to Vercel.

---

[View Full Sitemap](https://vercel.com/docs/sitemap)

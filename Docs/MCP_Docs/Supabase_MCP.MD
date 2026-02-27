# Supabase via MCP

Connect your AI tools to Supabase using the [Model Context Protocol (MCP)](https://modelcontextprotocol.io). Once connected, your AI assistants can interact with and query your Supabase projects on your behalf.

---

## What is Supabase MCP?

The Supabase MCP server is a remote server that allows AI agents (like Cursor, Claude Code, or Gemini) to securely perform database operations, manage edge functions, and search documentation.

**Official Endpoint:** `https://mcp.supabase.com/mcp`

---

## Setup

Choose your preferred AI client and follow the installation instructions.

### Cursor
Add this configuration to your project-specific or global `.cursor/mcp.json` file:
```json
{
  "mcpServers": {
    "supabase": {
      "url": "https://mcp.supabase.com/mcp"
    }
  }
}
```

### Claude Code
Add the MCP server to your project config using the command line:
```bash
claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp"
```
After configuring, authenticate by running:
```bash
claude /mcp
```
Select the **supabase** server and follow the OAuth flow in your browser.

### Gemini CLI
Ensure you are running version **0.20.2** or higher. Install the extension:
```bash
gemini extensions install https://github.com/supabase-community/gemini-extension
```
Or add the server manually to `.gemini/settings.json`:
```json
{
  "mcpServers": {
    "supabase": {
      "httpUrl": "https://mcp.supabase.com/mcp"
    }
  }
}
```

### Windsurf
Add this configuration to `~/.codeium/windsurf/mcp_config.json`:
```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.supabase.com/mcp"
      ]
    }
  }
}
```
> [!NOTE]
> Windsurf requires the `mcp-remote` package as a proxy for remote HTTP servers.

---

## Configuration Options

You can customize the server behavior using URL query parameters in your endpoint:

| Parameter | Description | Example |
| :--- | :--- | :--- |
| `read_only=true` | Execute queries as a read-only Postgres user. | `?read_only=true` |
| `project_ref=<id>` | Scope to a specific project (disables account tools). | `?project_ref=abc123` |
| `features=<groups>` | Enable specific tool groups (comma-separated). | `?features=database,docs` |

**Combined Example:** `https://mcp.supabase.com/mcp?project_ref=abc123&read_only=true`

---

## Available Tools

The Supabase MCP server organizes tools into feature groups. Most are enabled by default.

### Database management
- **`list_tables`**: List all tables in the database.
- **`list_extensions`**: List available/installed Postgres extensions.
- **`list_migrations`**: List database migrations.
- **`apply_migration`**: Apply a database migration.
- **`execute_sql`**: Execute raw SQL queries.

### Debugging & Monitoring
- **`get_logs`**: Retrieve service logs (API, Postgres, Functions, Auth, Storage, Realtime).
- **`get_advisors`**: Get security and performance advisory notices.

### Development Utilities
- **`get_project_url`**: Get the API URL for the project.
- **`get_publishable_keys`**: Get anon/public API keys.
- **`generate_typescript_types`**: Generate TypeScript types from your schema.

### Edge Functions
- **`list_edge_functions`**: List all deployed functions.
- **`get_edge_function`**: Retrieve details for a specific function.
- **`deploy_edge_function`**: Deploy code to an Edge Function.

### Account & Project Management
- **`list_projects` / `get_project`**: Manage your Supabase projects.
- **`create_project` / `pause_project` / `restore_project`**: Project lifecycle management.
- **`list_organizations`**: List accessible organizations.

### Specialized Tools
- **`search_docs`**: Search the Supabase documentation via GraphQL.
- **`create_branch` / `list_branches`**: Manage development branches (Experimental).

---

## Security Best Practices

> [!CAUTION]
> **Data Exposure:** Connecting an LLM to your database carries risks. Injected instructions in your database content (e.g., a support ticket) could trick an AI agent into exfiltrating data.

### Recommendations
- **Don't connect to Production:** Use development or staging projects with non-production data.
- **Read-Only Mode:** Use `?read_only=true` if you only need to query data.
- **Project Scoping:** Always scope the server to a specific `project_ref` to limit the AI's blast radius.
- **Human Confirmation:** Never disable "Always ask before running tools" in your MCP client.
- **Use Branching:** Use Supabase's branching feature to test changes in isolated environments.

---

## Manual Authentication (CI/Advanced)

If browser-based OAuth is not possible (e.g., in a CI environment), use a **Personal Access Token (PAT)**:

1. Generate a token in [Supabase Access Tokens](https://supabase.com/dashboard/account/tokens).
2. Pass the token in the `Authorization` header:

```json
{
  "headers": {
    "Authorization": "Bearer YOUR_SUPABASE_PAT"
  }
}
```

---

[View Project on GitHub](https://github.com/supabase-community/supabase-mcp)

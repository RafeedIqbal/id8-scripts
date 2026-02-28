# GitHub via MCP

Connect your AI tools to GitHub using the [Model Context Protocol (MCP)](https://modelcontextprotocol.io), an open standard that gives AI agents and assistants secure access to repositories, issues, pull requests, and more.

---

## Overview

The GitHub MCP Server allows AI tools to:
- **Browse and query code**: Search files, analyze commits, and understand project structure.
- **Manage Issues & PRs**: Create, update, and triage bugs or review code changes.
- **Monitor Workflows**: Analyze GitHub Actions runs and build failures.
- **Code Security**: Examine security findings and Dependabot alerts.
- **Collaborate**: Access discussions and manage team notifications.

---

## Remote GitHub MCP Server

The remote server is hosted by GitHub and is the easiest way to get started. It supports OAuth and provides high performance.

### Prerequisites
- A compatible MCP host (VS Code 1.101+, Claude Desktop, Cursor, Windsurf, etc.).
- GitHub account with necessary permissions.

### Setup in VS Code
The easiest way to install is via the VS Code interface or by adding the configuration manually:

| Authentication Method | Configuration Snippet |
| :--- | :--- |
| **OAuth (Recommended)** | ```json { "servers": { "github": { "type": "http", "url": "https://api.githubcopilot.com/mcp/" } } } ``` |
| **GitHub PAT** | ```json { "servers": { "github": { "type": "http", "url": "https://api.githubcopilot.com/mcp/", "headers": { "Authorization": "Bearer ${input:github_mcp_pat}" } } } } ``` |

> [!NOTE]
> For PAT authentication, you'll need to define a `promptString` input for `github_mcp_pat` in your host configuration.

---

## Local GitHub MCP Server

If your environment doesn't support remote HTTP servers, you can run a local instance via Docker or by building from source.

### Prerequisites
- **Docker**: Installed and running.
- **GitHub PAT**: A Personal Access Token with appropriate scopes.

### Docker Configuration
Add this to your MCP settings:
```json
{
  "github": {
    "command": "docker",
    "args": [
      "run",
      "-i",
      "--rm",
      "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
      "ghcr.io/github/github-mcp-server"
    ],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_PAT"
    }
  }
}
```

> [!CAUTION]
> **Token Security:** Never hardcode your PAT in a file that is committed to version control. Use environment variables or prompt inputs where possible.

---

## Configuration Options

### Toolsets
Limit the capabilities of the AI by specifying toolsets. This improves performance and security by reducing the tool choice scope.

- **Command Line:** `--toolsets repos,issues,pull_requests`
- **Environment Variable:** `GITHUB_TOOLSETS="repos,issues"`

> [!TIP]
> Use `GITHUB_TOOLSETS="all"` to enable everything, or `"default"` for the standard suite (context, repos, issues, pull_requests, users).

### Features

| Feature | Flag / Env Var | Description |
| :--- | :--- | :--- |
| **Read-Only Mode** | `--read-only` | Disables all write operations. |
| **Lockdown Mode** | `--lockdown-mode` | Limits content to authors with push access. |
| **Insiders Mode** | `--insiders` | Early access to experimental features. |
| **Dynamic Discovery** | `--dynamic-toolsets` | (Beta) Enable toolsets on the fly based on prompts. |

---

## Available Toolsets

| Icon | Toolset | Description |
| :--- | :--- | :--- |
| 👤 | `context` | **Recommended**: Current user and operating context. |
| ⚙️ | `actions` | GitHub Actions & CI/CD. |
| 🛡️ | `code_security` | Code Scanning & security events. |
| 🤖 | `copilot` | Copilot-specific tools. |
| 📦 | `dependabot` | Dependabot alerts and management. |
| 💬 | `discussions` | GitHub Discussions. |
| 📦 | `gists` | Gist management. |
| 🎋 | `git` | Low-level Git operations. |
| 🎫 | `issues` | Issue tracking and management. |
| 🏷️ | `labels` | Label management. |
| 🔔 | `notifications` | User notifications. |
| 🏢 | `orgs` | Organization management. |
| 📊 | `projects` | GitHub Projects (v2). |
| 🔀 | `pull_requests` | Pull Request lifecycle. |
| 📂 | `repos` | Repository management. |

---

## Tool Reference

Detailed breakdown of top-level tools available via the GitHub MCP server.

<details>
<summary>📂 Repository Tools</summary>

- **`get_file_contents`**: Read files or directory structures.
- **`create_or_update_file`**: Commit changes to a file.
- **`create_repository`**: Create a new repo.
- **`search_code`**: Use GitHub's advanced code search.
- **`push_files`**: Multiple file commit in one go.
</details>

<details>
<summary>🎫 Issue & PR Tools</summary>

- **`issue_read`**: Fetch issue details and comments.
- **`issue_write`**: Create or update issues.
- **`create_pull_request`**: Open a new PR.
- **`merge_pull_request`**: Complete a PR.
- **`pull_request_read`**: Review code changes and comments.
</details>

<details>
<summary>⚙️ Actions & CI Tools</summary>

- **`actions_list`**: List workflows and runs.
- **`actions_run_trigger`**: Start a workflow run manually.
- **`get_job_logs`**: Retrieve logs for debugging.
</details>

<details>
<summary>👤 Context & User Tools</summary>

- **`get_me`**: Identify current user.
- **`get_teams`**: List user's teams and organizations.
</details>

---

## Security Best Practices

> [!IMPORTANT]
> **Access Control:** Connecting an AI to GitHub grants it significant power. Follow these rules to stay secure.

1. **Least Privilege**: Only provide a PAT with the minimum scopes needed.
2. **Read-Only by Default**: Use `--read-only` for research or analysis tasks.
3. **Environment Isolation**: Prefer connecting to development forks rather than production mission-critical repos.
4. **Human in the Loop**: Always review PRs, issues, and code changes generated by an AI before merging.

---

[View Project on GitHub](https://github.com/github/github-mcp-server)
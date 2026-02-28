# Context7 via MCP

Connect your AI tools to [Context7](https://context7.com) using the Model Context Protocol (MCP). Context7 pulls up-to-date, version-specific documentation and code examples directly from the source and injects them into your prompt context.

---

## Overview

Context7 eliminates documentation hallucinations by providing LLMs with real-time access to:
- **Up-to-date APIs**: No more outdated generated code.
- **Version-Specific Docs**: Handle breaking changes between library versions effortlessly.
- **Code Examples**: Real-world templates pulled straight from official sources.

Simply append `use context7` to your prompt to invoke it.

---

## Setup

> [!TIP]
> **API Key Recommended:** Get a free API key at [context7.com/dashboard](https://context7.com/dashboard) for significantly higher rate limits and personal library access.

### Automatic Setup
The simplest way to configure Context7 for your environment:
```bash
npx ctx7 setup
```
This tool handles OAuth, generates an API key, and configures the MCP server for Cursor, Claude, or VS Code automatically.

### Manual Configuration

| Method | Configuration Snippet |
| :--- | :--- |
| **Remote (OAuth)** | ```json { "url": "https://mcp.context7.com/mcp/oauth" } ``` |
| **Remote (Shared)** | ```json { "url": "https://mcp.context7.com/mcp", "headers": { "CONTEXT7_API_KEY": "YOUR_API_KEY" } } ``` |
| **Local (stdio)** | ```json { "command": "npx", "args": ["-y", "@upstash/context7-mcp", "--api-key", "YOUR_API_KEY"] } ``` |

---

## Best Practices

### Configure an Auto-Rule
To avoid typing `use context7` repeatedly, add a system rule to your client (e.g., in `.cursorrules` or `CLAUDE.md`):

```txt
Always use Context7 MCP when I need library/API documentation, code generation, or configuration steps without me having to explicitly ask.
```

### Targeted Queries
For faster and more accurate results, use the library ID syntax:
- **Specific Library:** `Implement auth with /supabase/supabase. use context7`
- **Specific Version:** `How do I set up Next.js 14 middleware? use context7`

---

## Available Tools

| Tool | Description |
| :--- | :--- |
| **`resolve-library-id`** | Maps a generic library name (e.g., "React") to a Context7 ID. |
| **`query-docs`** | Searches the documentation for specific answers and code snippets. |

---

## Security & Reliability

> [!IMPORTANT]
> **Trust and Verification:** Context7 projects are community-contributed. While we strive for accuracy, always verify mission-critical code generated from third-party documentation.

- **OAuth Support**: Use the `/mcp/oauth` endpoint for clients that support the MCP OAuth 2.0 specification for enhanced security.
- **Data Privacy**: Context7 only fetches public documentation or private docs authorized via your API key.

---

[View Project Website](https://context7.com) | [Discord Community](https://upstash.com/discord) | [Full Documentation](https://context7.com/docs)
# Stitch via MCP

Connect IDEs and CLIs to Stitch using the Model Context Protocol (MCP).

The Stitch MCP server allows your favorite AI tools like **Cursor**, **Antigravity**, or the **Gemini CLI** to directly interact with your Stitch projects.

---

## Understanding Remote MCP

Most MCP servers you use are **Local**. They read files on your hard drive or run scripts on your machine. **Stitch is a Remote MCP server.** It lives in the cloud.

Because it is remote, it requires a secure “handshake” to ensure that the AI agent acting on your behalf actually has permission to modify your designs.

---

## Authentication: API Keys vs OAuth

The Stitch MCP server supports two authentication methods:

1.  **API Keys:** Persistent keys generated in the Stitch Settings page.
2.  **OAuth:** A browser-based authentication flow required by specific AI clients that do not support manual key entry, or for environments where storing persistent secrets on disk is restricted.

### When to use which?

In most cases, **API Keys** are the easiest approach and the fastest way to get connected. However, **OAuth** is worth the extra setup in specific situations.

| Scenario | Use API Keys if... | Use OAuth if... |
| :--- | :--- | :--- |
| **Client Support** | Your tool (e.g., Cursor, Antigravity, or the Gemini CLI) accepts an API key in a config file or environment variable. | Your tool (e.g., web-based tools) requires a “Sign In” flow and doesn’t provide a way to manually input a key. |
| **Storage Policy** | You are on a private machine where saving a secret key in a local `.json` or `.env` file is standard practice. | You are in a “Zero-Trust” or ephemeral environment where saving persistent secrets to the hard drive is blocked or risky. |
| **Revocation** | You are comfortable manually deleting a key from the Stitch Settings page and then finding/removing it from your local files. | You want the ability to “Log Out” and instantly invalidate the tool’s access via the Stitch Settings page without hunting for local files. |
| **Session Logic** | You want a connection that stays active indefinitely until you manually change it. | You prefer a session-based connection that can be set to expire or require a re-approval after a period of inactivity. |

---

## API Key Setup

1.  Go to your **Stitch Settings** page.
2.  Scroll to the **API Keys** section.
3.  Click on **“Create API Key”** to generate a new key.
4.  Copy the API key and save it in a secure location.

> [!CAUTION]
> **Storing API Keys:** Never store your API key in a place where it can be exposed to the public. Never commit your API key to a public repository. Don’t include your API key in client-side code that can be viewed by others.

---

## MCP Client Setup (API Key)

### Gemini CLI
Install the Stitch extension for the Gemini CLI:
```bash
gemini extensions install https://github.com/gemini-cli-extensions/stitch
```

### Cursor
Create a `.cursor/mcp.json` file with the following entry:
```json
{
  "mcpServers": {
    "stitch": {
      "url": "https://stitch.googleapis.com/mcp",
      "headers": {
        "X-Goog-Api-Key": "YOUR-API-KEY"
      }
    }
  }
}
```

### Antigravity
In the Agent Panel, click the three dots in the top right and select **MCP Servers**. Click **Manage MCP Servers**. Select **“View raw config”** and add the following entry:
```json
{
  "mcpServers": {
    "stitch": {
      "serverUrl": "https://stitch.googleapis.com/mcp",
      "headers": {
        "X-Goog-Api-Key": "YOUR-API-KEY"
      }
    }
  }
}
```

### VSCode
1.  Open the Command Palette (`Cmd+Shift+P`) and type **“MCP: Add Server”**.
2.  Select **“Add MCP Server”**.
3.  Select **HTTP** to add a remote MCP server.
4.  Enter the Stitch MCP URL: `https://stitch.googleapis.com/mcp`.
5.  Set the name to `stitch` and confirm.

Then modify the `mcp.json` file to add the API key:
```json
{
  "servers": {
    "stitch": {
      "url": "https://stitch.googleapis.com/mcp",
      "type": "http",
      "headers": {
        "Accept": "application/json",
        "X-Goog-Api-Key": "YOUR-API-KEY"
      }
    }
  }
}
```

### Claude Code
Use the `claude mcp` command to authenticate and add the following entry:
```bash
claude mcp add stitch --transport http https://stitch.googleapis.com/mcp --header "X-Goog-Api-Key: api-key" -s user
```

---

## OAuth Setup

To allow your MCP Client to talk to Stitch via OAuth, you need to generate:
- **Project ID:** The container for your work.
- **Access Token:** A short-lived key to verify authentication.

### 1. Install the Google Cloud SDK
Stitch relies on the `gcloud` CLI for secure authentication.

#### Standalone
```bash
# Download and install
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Set local configuration to avoid prompts
export CLOUDSDK_CORE_DISABLE_PROMPTS=1
```

#### Homebrew
```bash
brew install --cask google-cloud-sdk
```

### 2. Double-Layer Authentication
You need to log in twice: once as **You** (user) and once as the **Application** (local code).

```bash
# 1. User Login (Opens Browser)
gcloud auth login

# 2. Application Default Credentials (ADC) Login
# This allows the MCP server to "impersonate" you securely.
gcloud auth application-default login
```

### 3. Configure the Project & Permissions
Select your working project and enable the Stitch API.

```bash
# Replace [YOUR_PROJECT_ID] with your actual Google Cloud Project ID
PROJECT_ID="[YOUR_PROJECT_ID]"

gcloud config set project "$PROJECT_ID"

# Enable the Stitch API
gcloud beta services mcp enable stitch.googleapis.com --project="$PROJECT_ID"

# Grant Service Usage Consumer role
USER_EMAIL=$(gcloud config get-value account)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="user:$USER_EMAIL" \
    --role="roles/serviceusage.serviceUsageConsumer" \
    --condition=None
```

### 4. Generate the Secrets (.env)
Generate the Access Token and save it to a `.env` file.

```bash
# Print the token
TOKEN=$(gcloud auth application-default print-access-token)

# Note: This overwrites any existing .env file
echo "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" > .env
echo "STITCH_ACCESS_TOKEN=$TOKEN" >> .env

echo "Secrets generated in .env"
```

### 5. Keeping it Fresh
> [!IMPORTANT]
> **Access Tokens are temporary** (usually lasting 1 hour). When your MCP client stops responding or says “Unauthenticated,” you need to:
> 1. Re-run the commands in Step 4 to update your `.env` file.
> 2. Copy the new `STITCH_ACCESS_TOKEN` value into your MCP client config.

---

## MCP Client Setup (OAuth)

Copy the values from `.env` into your configuration:
- `<YOUR_PROJECT_ID>` → Value of `GOOGLE_CLOUD_PROJECT`
- `<YOUR_ACCESS_TOKEN>` → Value of `STITCH_ACCESS_TOKEN`

### Cursor
```json
{
  "mcpServers": {
    "stitch": {
      "url": "https://stitch.googleapis.com/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_ACCESS_TOKEN>",
        "X-Goog-User-Project": "<YOUR_PROJECT_ID>"
      }
    }
  }
}
```

### Antigravity
```json
{
  "mcpServers": {
    "stitch": {
      "serverUrl": "https://stitch.googleapis.com/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_ACCESS_TOKEN>",
        "X-Goog-User-Project": "<YOUR_PROJECT_ID>"
      }
    }
  }
}
```

### VSCode
Modify the `mcp.json` file:
```json
{
  "servers": {
    "stitch": {
      "url": "https://stitch.googleapis.com/mcp",
      "type": "http",
      "headers": {
        "Accept": "application/json",
        "Authorization": "Bearer <YOUR_ACCESS_TOKEN>",
        "X-Goog-User-Project": "<YOUR_PROJECT_ID>"
      }
    }
  }
}
```

### Claude Code
```bash
claude mcp add stitch \
  --transport http https://stitch.googleapis.com/mcp \
  --header "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  --header "X-Goog-User-Project: <YOUR_PROJECT_ID>" \
  -s user
```

---

## Available Tools

Once authenticated, your AI assistant will have access to the following tools.

### Project Management
-   **`create_project`**: Creates a new container for your UI work.
    -   `title` (string): Optional display name.
-   **`list_projects`**: Retrieves a list of all active designs.
    -   `filter` (string): Filters by `view=owned` or `view=shared`.
-   **`get_project`**: Retrieves specific details for a single project.
    -   `name` (string): The unique resource name (`projects/{id}`).

### Screen Management
-   **`list_screens`**: Fetches all screens within a specific project.
    -   `projectId` (string): The ID of the project to inspect.
-   **`get_screen`**: Retrieves specific details for a single screen.
    -   `name` (string): Resource name (`projects/{p}/screens/{s}`).
    -   `projectId` (string): (Deprecated)
    -   `screenId` (string): (Deprecated)

### AI Generation
-   **`generate_screen_from_text`**: Creates a new design from a text prompt.
    -   `prompt` (string): Description of the screen.
    -   `modelId`: `GEMINI_3_PRO` or `GEMINI_3_FLASH`.
-   **`edit_screens`**: Edits existing screens using instructions.
-   **`generate_variants`**: Generates design variants of existing screens.
-   **`upload_screens_from_images`**: Uploads images to create new screens.

---

## Getting Started: A Workflow Example

The Stitch MCP takes the power of generating designs from within the Stitch editor and brings it into your IDE or CLI. You can convert designs into code and generate new screens automatically.

### 1. "Show me my projects"
Ask the agent to see your Stitch Projects and screens.

> **Prompt:** "Show me my Stitch projects. List out each screen under each project and its screen id."

**Example Response:**
1. **Raffinato Coffee Store App** (Desktop, Light Mode)
   - Screens: `Home Menu`, `Full Menu`, `Checkout`

### 2. "Convert to Code"
Once the agent knows which screen to work with, you can request the code.

> **Prompt:** "Download the HTML code for the Full Menu screen in the Raffinato project. Create a file named `./tmp/full-menu.html`."

The HTML file will include a complete document with a **Tailwind CSS** configuration specific to that design.

### 3. "HTML to React/Flutter/Compose"
LLMs excel at converting this foundation into high-quality components for any framework.

---

## Creating a React Component System

You can use the `add-skill` library to install specific agent skills for Stitch.

```bash
npx add-skill google-labs-code/stitch-skills --skill react:components --global
```

This skill teaches the agent how to use Stitch tools to generate a well-structured React app (e.g., using Vite).

> **Prompt:** "Convert the Landing Page screen in the Podcast Project to React components."

---

## Tool Reference

| # | Tool | Category | Read-Only |
| :- | :--- | :--- | :--- |
| 1 | `create_project` | Project Management | ✗ |
| 2 | `get_project` | Project Management | ✓ |
| 3 | `delete_project` | Project Management | ✗ |
| 4 | `list_projects` | Project Management | ✓ |
| 5 | `list_screens` | Screen Management | ✓ |
| 6 | `get_screen` | Screen Management | ✓ |
| 7 | `generate_screen_from_text` | AI Generation | ✗ |
| 8 | `upload_screens_from_images` | AI Generation | ✗ |
| 9 | `edit_screens` | AI Generation | ✗ |
| 10 | `generate_variants` | AI Generation | ✗ |
| 11 | `create_design_system` | Design Systems | ✗ |
| 12 | `update_design_system` | Design Systems | ✗ |
| 13 | `list_design_systems` | Design Systems | ✓ |
| 14 | `apply_design_system` | Design Systems | ✗ |

---

## Data Model & Types

### Screen
Represents a generated screen design.

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | string | `projects/{project}/screens/{screen}` |
| `title` | string | Display title. |
| `screenshot` | File | Image reference. |
| `htmlCode` | File | HTML code reference. |
| `theme` | DesignTheme | Applied theme. |
| `deviceType` | Enum | `MOBILE`, `DESKTOP`, etc. |

### DesignTheme
| Field | Required | Description |
| :--- | :--- | :--- |
| `colorMode` | Yes | `LIGHT` or `DARK`. |
| `font` | Yes | Typography selection. |
| `roundness` | Yes | Corner roundness. |
| `preset` | Yes | Base color name. |

### Available Fonts
`INTER` · `ROBOTO` · `DM_SANS` · `GEIST` · `SORA` · `MANROPE` · `LEXEND` · `EPILOGUE` · `BE_VIETNAM_PRO` · `PLUS_JAKARTA_SANS` · `PUBLIC_SANS` · `SPACE_GROTESK` · `SPLINE_SANS` · `WORK_SANS` · `MONTSERRAT` · `METROPOLIS` · `SOURCE_SANS_THREE` · `NUNITO_SANS` · `ARIMO` · `HANKEN_GROTESK` · `RUBIK` · `IBM_PLEX_SANS` · `NEWSREADER` · `NOTO_SERIF` · `DOMINE` · `LIBRE_CASLON_TEXT` · `EB_GARAMOND` · `LITERATA` · `SOURCE_SERIF_FOUR`

### Other Enums

#### DeviceType
`DEVICE_TYPE_UNSPECIFIED` · `MOBILE` · `DESKTOP` · `TABLET` · `AGNOSTIC`

#### ModelId
`MODEL_ID_UNSPECIFIED` · `GEMINI_3_PRO` · `GEMINI_3_FLASH`

#### ScreenType
`SCREEN_TYPE_UNSPECIFIED` · `DESIGN` · `IMAGE` · `PROTOTYPE` · `DOCUMENT`

#### Roundness
`ROUNDNESS_UNSPECIFIED` · `ROUND_FOUR` · `ROUND_EIGHT` · `ROUND_TWELVE` · `ROUND_FULL`

#### CreativeRange
`CREATIVE_RANGE_UNSPECIFIED` · `REFINE` · `EXPLORE` (Default) · `REIMAGINE`

#### VariantAspect
`LAYOUT` · `COLOR_SCHEME` · `IMAGES` · `TEXT_FONT` · `TEXT_CONTENT`

---

## MCP Annotations (Behavior Hints)

Stitch tools include behavior hints to help AI clients manage operations:

-   **`readOnlyHint`**: `true` for fetching data; can be auto-approved.
-   **`destructiveHint`**: `true` for mutations; clients should prompt for confirmation.
-   **`idempotentHint`**: `true` if repeated calls are safe.
-   **`openWorldHint`**: `false` for Stitch tools (they only talk to Stitch backend).

### Why they matter:
-   **Auto-approval** for read-only tools.
-   **Confirmation dialogs** for projects/screen deletion.
-   **Safety** when retrying generation tasks.
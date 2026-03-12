# llm-sync-drive

Compile your repository into a structured `llms.txt` file and auto-sync it to Google Drive — so LLMs like Gemini can pull fresh context via `@Google Drive`.

## What It Does

1. **Compiles** your repo into a single structured Markdown document (directory tree + file contents)
2. **Respects** `.gitignore` and `.llmsignore` to exclude noise, secrets, and binaries
3. **Uploads** to a single Google Drive file (idempotent — same link every time)
4. **Watches** for changes and re-syncs automatically with configurable debounce

## Quick Start

### 1. Install

```bash
pip install -e .
```

### 2. Set Up Google Drive API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use an existing one)
3. Navigate to **APIs & Services → Library**, search for **Google Drive API**, and **Enable** it

#### Option A: Application Default Credentials (Recommended — simplest)

4. Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install) if you don't have it
5. Run:
   ```bash
   gcloud auth application-default login --scopes="https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/cloud-platform"
   ```
6. A browser opens for consent — sign in with your Google account
7. Done. No credentials file needed. ADC token is cached at `%APPDATA%/gcloud/application_default_credentials.json` (Windows) or `~/.config/gcloud/application_default_credentials.json` (macOS/Linux)

#### Option B: Service Account (headless key file)

4. Go to **APIs & Services → Credentials**
5. Click **+ Create Credentials → Service account**
6. Name it (e.g., `mcp-drive-sync`) and click **Create and Continue**, then **Done**
7. Copy the service account email (e.g., `mcp-drive-sync@your-project.iam.gserviceaccount.com`)
8. Click the service account → **Keys** tab → **Add Key → Create new key → JSON**
9. Save the downloaded file as `credentials.json` in your repo directory
10. In your **personal Google Drive**, create a folder (e.g., `MCP-Context-Sync`)
11. **Share** that folder with the service account email (Editor permissions)
12. Copy the **Folder ID** from the folder's URL (the string after `folders/`)

#### Option C: OAuth 2.0 (Interactive, for CLI use)

4. Go to **APIs & Services → OAuth consent screen**, set to External, add your email as a test user
5. Go to **Credentials → + Create Credentials → OAuth client ID** (Desktop app)
6. Download the JSON and save it as `credentials.json`

### 3. Initialize Config

```bash
cd /path/to/your/repo
llm-sync-drive init --repo .
```

This creates `llm-sync-drive.yaml`. Edit it to set:

- `auth_mode`: `"adc"` (default), `"service-account"`, or `"oauth"`
- `credentials_path`: path to your `credentials.json` (service-account/oauth modes only)
- `drive_folder_id`: the Google Drive folder ID (from the folder's URL)
- `project_description`: a one-liner about your project

### 4. Authenticate (OAuth only)

If using OAuth mode, run:

```bash
llm-sync-drive auth
```

Opens a browser for consent. The token is cached in `token.json`. ADC and service account modes need no auth step.

### 5. Sync Once

```bash
llm-sync-drive sync
```

Compiles and uploads. The Drive file ID is saved to your config automatically.

### 6. Watch Mode

```bash
llm-sync-drive serve
```

Runs an initial sync, then watches the repo. After files stop changing for the debounce interval (default 5s), it recompiles and uploads.

### 7. Local Preview

```bash
llm-sync-drive compile -o llms.txt
```

Compiles to a local file without uploading. Useful for inspection.

## MCP Server (AI Assistant Integration)

llm-sync-drive runs as an **MCP (Model Context Protocol) server**, so AI assistants like GitHub Copilot can sync your repos to Drive directly during a conversation.

### VS Code Setup

Add to your VS Code user settings or workspace `.vscode/mcp.json`:

```json
{
  "servers": {
    "llm-sync-drive": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "llm_sync_drive.server"]
    }
  }
}
```

Or set environment variables for config-free operation:

```json
{
  "servers": {
    "llm-sync-drive": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "llm_sync_drive.server"],
      "env": {
        "LLM_SYNC_DRIVE_CONFIG": "F:/AI/my-project/llm-sync-drive.yaml"
      }
    }
  }
}
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `sync_to_drive` | Compile repo + upload to Drive. Use after each phase/milestone. |
| `compile_context` | Compile locally without uploading (preview or save snapshot). |
| `sync_status` | Check config, Drive file ID, auth status. |
| `list_repos` | Find repos with existing sync configs. |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `LLM_SYNC_DRIVE_CONFIG` | Path to config YAML (auto-discovered in repo root otherwise) |
| `LLM_SYNC_DRIVE_FILE_ID` | Drive file ID (override config) |
| `LLM_SYNC_DRIVE_FOLDER_ID` | Drive folder ID (override config) |
| `LLM_SYNC_DRIVE_CREDENTIALS` | Path to credentials.json (override config) |
| `LLM_SYNC_DRIVE_TOKEN` | Path to token.json (override config) |

## Configuration

All options live in `llm-sync-drive.yaml`:

| Key | Description | Default |
|-----|-------------|---------|
| `repo_path` | Path to the repository | required |
| `auth_mode` | `"adc"` (simplest), `"service-account"` (key file), or `"oauth"` (interactive) | `adc` |
| `credentials_path` | Service account key or OAuth credentials JSON | `credentials.json` |
| `token_path` | Cached OAuth token (oauth mode only) | `token.json` |
| `drive_folder_id` | Drive folder to upload into | `null` |
| `drive_file_id` | Drive file ID (auto-set after first upload) | `null` |
| `drive_filename` | Filename in Drive | `llms.txt` |
| `local_output` | Also save locally | `null` |
| `project_description` | Header text in compiled output | `""` |
| `debounce_seconds` | Wait time after last change | `5.0` |
| `max_file_bytes` | Skip files larger than this | `100000` |
| `include_extensions` | Only include these extensions | `[]` (all text files) |
| `extra_ignore_patterns` | Additional patterns to ignore | `[]` |

## Ignore Rules

Files are excluded (in order) by:

1. **Built-in rules**: `.git/`, `node_modules/`, `__pycache__/`, lock files, secret files
2. **`.gitignore`**: Standard git ignore patterns
3. **`.llmsignore`**: Additional patterns specific to LLM context (e.g., test fixtures, binary assets)
4. **`extra_ignore_patterns`** in config

See `.llmsignore.example` for a starter template.

## Output Format

The compiled `llms.txt` follows this structure:

```markdown
# project-name

> Auto-generated by llm-sync-drive on 2026-03-12 18:00 UTC
> Source: /path/to/repo
> Files included: 42

## Directory Structure

​```
src/
  index.ts
  utils/
    helpers.ts
​```

## File Contents

### src/index.ts

​```ts
// file contents here
​```
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `llm-sync-drive init` | Create default config file |
| `llm-sync-drive auth` | Authenticate with Google Drive |
| `llm-sync-drive sync` | One-shot compile + upload |
| `llm-sync-drive serve` | Watch mode with auto-sync |
| `llm-sync-drive compile` | Compile locally (no upload) |

All commands accept `-v` / `--verbose` for debug logging.

## Security Notes

- **`credentials.json`** and **`token.json`** are in `.gitignore` — never commit them
- The app uses `drive.file` scope (can only access files it creates, not your entire Drive)
- `.llmsignore` provides defense-in-depth against leaking secrets into the compiled output
- Built-in rules always exclude `.env`, `*.key`, `*.pem`, etc.

## License

MIT

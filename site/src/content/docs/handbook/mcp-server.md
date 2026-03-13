---
title: MCP Server
description: Use llm-sync-drive as a Model Context Protocol server for AI assistant integration.
sidebar:
  order: 4
---

llm-sync-drive runs as a **Model Context Protocol (MCP) server**, allowing AI assistants like GitHub Copilot, Claude, and others to sync your repos to Drive directly during a conversation.

## VS Code setup

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

To point at a specific config without needing to be in the repo directory:

```json
{
  "servers": {
    "llm-sync-drive": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "llm_sync_drive.server"],
      "env": {
        "LLM_SYNC_DRIVE_CONFIG": "/path/to/llm-sync-drive.yaml"
      }
    }
  }
}
```

## Available tools

| Tool | Description |
|------|-------------|
| `sync_to_drive` | Compile repo + upload to Drive. Use after each phase or milestone. |
| `compile_context` | Compile locally without uploading. Good for previewing or saving a snapshot. |
| `sync_status` | Check config, Drive file ID, and auth status. |
| `list_repos` | Find repos with existing `llm-sync-drive.yaml` configs. |

## Typical workflow

1. Start a coding session with an AI assistant
2. The assistant calls `sync_to_drive` to push fresh context to Drive
3. Reference the Drive file in Gemini or another LLM via `@Google Drive`
4. After completing a milestone, sync again to keep the context current

## Config resolution

The MCP server resolves config in this order:

1. Explicit `config_path` parameter passed to the tool
2. `LLM_SYNC_DRIVE_CONFIG` environment variable
3. `llm-sync-drive.yaml` in the specified `repo_path`
4. `llm-sync-drive.yaml` in the current working directory

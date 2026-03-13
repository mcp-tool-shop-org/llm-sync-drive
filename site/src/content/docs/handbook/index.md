---
title: Welcome
description: llm-sync-drive compiles your repository into a structured llms.txt file and syncs it to Google Drive for LLM consumption.
sidebar:
  order: 0
---

**llm-sync-drive** turns your codebase into a single structured document and keeps it synced to Google Drive — so LLMs like Gemini can pull fresh context via `@Google Drive`.

## Why?

Large language models work best when they have full project context. But feeding an entire repo into a prompt is noisy — lock files, binaries, build artifacts, and secrets all get in the way.

llm-sync-drive solves this by:

1. **Compiling** your repo into a clean `llms.txt` Markdown document (directory tree + file contents)
2. **Filtering** noise via `.gitignore`, `.llmsignore`, and built-in rules
3. **Uploading** to a single Google Drive file with an idempotent link
4. **Watching** for changes and re-syncing automatically

The result is a single Drive URL that always has your latest repo context — ready for any LLM that can read from Google Drive.

## How it works

```
your-repo/
  src/
  tests/
  README.md
  ...
        ↓  compile
llms.txt (structured Markdown)
        ↓  upload
Google Drive (single file, same URL)
        ↓  reference
LLM reads fresh context via @Google Drive
```

## Next steps

- [Getting Started](/llm-sync-drive/handbook/getting-started/) — install and authenticate
- [Usage](/llm-sync-drive/handbook/usage/) — CLI commands and watch mode
- [Configuration](/llm-sync-drive/handbook/configuration/) — all config options
- [MCP Server](/llm-sync-drive/handbook/mcp-server/) — AI assistant integration
- [Security](/llm-sync-drive/handbook/security/) — how your data stays safe

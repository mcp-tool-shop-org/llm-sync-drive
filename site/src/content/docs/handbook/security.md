---
title: Security
description: How llm-sync-drive protects your credentials and sensitive data.
sidebar:
  order: 5
---

## Credential safety

- **`credentials.json`** and **`token.json`** are in `.gitignore` by default — they should never be committed
- The tool generates a `.gitignore` entry during `init` if one doesn't exist
- Service account keys should be stored outside the repo when possible

## Minimal Drive scope

llm-sync-drive uses the `drive.file` scope, which means it can **only access files it creates** — not your entire Google Drive. This is the narrowest scope available for file upload.

## Defense-in-depth filtering

Sensitive files are excluded at multiple layers:

1. **Built-in ignores** always exclude:
   - `.env`, `.env.*`
   - `*.secret`, `*.key`, `*.pem`, `*.p12`, `*.pfx`
   - `credentials.json`, `token.json`
   - `.git/` contents

2. **`.gitignore`** rules are respected automatically

3. **`.llmsignore`** provides an additional layer for LLM-specific exclusions (test fixtures, large data files, binary assets)

4. **`extra_ignore_patterns`** in config for per-repo overrides

## What gets uploaded

Only text files that pass all four filter layers are included. Binary files, files exceeding `max_file_bytes`, and files matching any ignore pattern are excluded.

The compiled output contains:
- A directory tree showing included files
- The full text content of each included file

No metadata, git history, or system information is included in the output.

## Recommendations

- Review the output of `llm-sync-drive compile -o llms.txt` before your first sync to verify no sensitive data leaks through
- Use `.llmsignore` to exclude test fixtures, mock data, or anything that shouldn't reach an LLM
- For service account auth, store the key file outside the repository and reference it with an absolute path
- Rotate credentials periodically per your organization's security policy

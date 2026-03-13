---
title: Configuration
description: All configuration options for llm-sync-drive.yaml.
sidebar:
  order: 3
---

All configuration lives in `llm-sync-drive.yaml`, created by `llm-sync-drive init`.

## Config reference

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `repo_path` | string | *required* | Path to the repository (relative to config file, or absolute) |
| `auth_mode` | string | `"adc"` | `"adc"`, `"service-account"`, or `"oauth"` |
| `credentials_path` | string | `"credentials.json"` | Service account key or OAuth credentials JSON |
| `token_path` | string | `"token.json"` | Cached OAuth token (oauth mode only) |
| `drive_folder_id` | string | `null` | Google Drive folder to upload into |
| `drive_file_id` | string | `null` | Drive file ID (auto-set after first upload) |
| `drive_filename` | string | `"llms.txt"` | Filename in Google Drive |
| `local_output` | string | `null` | Also save a local copy at this path |
| `project_description` | string | `""` | Header text in compiled output |
| `debounce_seconds` | number | `5.0` | Wait time after last file change before syncing |
| `max_file_bytes` | number | `100000` | Skip files larger than this (bytes) |
| `include_extensions` | list | `[]` | Only include these extensions (empty = all text files) |
| `extra_ignore_patterns` | list | `[]` | Additional ignore patterns beyond .gitignore / .llmsignore |

## Environment variables

Environment variables override config file values:

| Variable | Description |
|----------|-------------|
| `LLM_SYNC_DRIVE_CONFIG` | Path to config YAML (auto-discovered in repo root otherwise) |
| `LLM_SYNC_DRIVE_FILE_ID` | Override Drive file ID |
| `LLM_SYNC_DRIVE_FOLDER_ID` | Override Drive folder ID |
| `LLM_SYNC_DRIVE_CREDENTIALS` | Override path to credentials.json |
| `LLM_SYNC_DRIVE_TOKEN` | Override path to token.json |

## Example config

```yaml
# Minimal config — ADC auth, auto-created Drive file
repo_path: "."
auth_mode: "adc"
drive_folder_id: "1ABCdefGHIjklMNOpqrSTUvwxYZ"
project_description: "My awesome project"
```

```yaml
# Full config — service account, extension filter, local output
repo_path: "/home/user/my-project"
auth_mode: "service-account"
credentials_path: "/etc/secrets/drive-sa.json"
drive_folder_id: "1ABCdefGHIjklMNOpqrSTUvwxYZ"
drive_filename: "my-project-context.txt"
local_output: "llms.txt"
project_description: "Backend API for widget service"
debounce_seconds: 10.0
max_file_bytes: 200000
include_extensions:
  - .py
  - .sql
  - .md
extra_ignore_patterns:
  - "*.log"
  - "migrations/"
```

## Path resolution

- `repo_path`: if relative, resolved relative to the config file's directory
- `credentials_path`, `token_path`, `local_output`: same resolution rules
- Absolute paths are used as-is

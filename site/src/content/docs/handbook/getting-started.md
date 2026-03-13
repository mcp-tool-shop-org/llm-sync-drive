---
title: Getting Started
description: Install llm-sync-drive, set up Google Drive API access, and run your first sync.
sidebar:
  order: 1
---

## Install

```bash
pip install llm-sync-drive
```

Or install from source for development:

```bash
git clone https://github.com/mcp-tool-shop-org/llm-sync-drive.git
cd llm-sync-drive
pip install -e .
```

## Set up Google Drive API

You need a Google Cloud project with the Drive API enabled. Go to the [Google Cloud Console](https://console.cloud.google.com/), create or select a project, then navigate to **APIs & Services > Library** and enable the **Google Drive API**.

llm-sync-drive supports three authentication modes. Pick the one that fits your workflow.

### Option A: Application Default Credentials (recommended)

The simplest option — uses your existing gcloud login. No credentials file needed.

1. Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install) if you don't have it
2. Run:
   ```bash
   gcloud auth application-default login \
     --scopes="https://www.googleapis.com/auth/drive.file,https://www.googleapis.com/auth/cloud-platform"
   ```
3. A browser opens for consent — sign in with your Google account
4. Done. The token is cached automatically.

### Option B: Service Account (headless / CI)

Best for automated pipelines and MCP server deployments where no browser is available.

1. Go to **APIs & Services > Credentials**
2. Click **+ Create Credentials > Service account**
3. Name it (e.g., `llm-sync-drive`) and click **Create and Continue**, then **Done**
4. Click the service account > **Keys** tab > **Add Key > Create new key > JSON**
5. Save the downloaded file as `credentials.json` in your repo directory
6. In Google Drive, create a folder and **share** it with the service account email (Editor permissions)
7. Copy the folder ID from the URL

### Option C: OAuth 2.0 (interactive)

For CLI use when you want per-user consent with a cached token.

1. Go to **APIs & Services > OAuth consent screen**, set to External, add your email as a test user
2. Go to **Credentials > + Create Credentials > OAuth client ID** (Desktop app)
3. Download the JSON and save it as `credentials.json`
4. Run `llm-sync-drive auth` to complete the browser consent flow

## Initialize a repo

```bash
cd /path/to/your/repo
llm-sync-drive init --repo .
```

This creates `llm-sync-drive.yaml`. Edit it to set your `auth_mode`, `drive_folder_id`, and `project_description`.

## First sync

```bash
llm-sync-drive sync
```

This compiles your repo into `llms.txt` and uploads it to Google Drive. The Drive file ID is saved to your config automatically — subsequent syncs update the same file (same URL every time).

"""Google Drive API integration — upload and update a single file."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2 import service_account as sa
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

log = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def authenticate(
    credentials_path: Path,
    token_path: Path,
    auth_mode: str = "service-account",
) -> Credentials | sa.Credentials:
    """Authenticate with Google Drive.

    auth_mode:
      - "service-account" (default): headless via JSON key file. Best for MCP/CI.
      - "oauth": interactive browser consent. Caches token for subsequent runs.
    """
    if auth_mode == "service-account":
        return _auth_service_account(credentials_path)
    return _auth_oauth(credentials_path, token_path)


def _auth_service_account(credentials_path: Path) -> sa.Credentials:
    """Authenticate headlessly via a service account JSON key."""
    if not credentials_path.exists():
        raise FileNotFoundError(
            f"Service account key not found: {credentials_path}\n"
            "Create one in Google Cloud Console → IAM & Admin → Service Accounts → Keys."
        )
    creds = sa.Credentials.from_service_account_file(str(credentials_path), scopes=SCOPES)
    log.info("Authenticated as service account: %s", creds.service_account_email)
    return creds


def _auth_oauth(credentials_path: Path, token_path: Path) -> Credentials:
    """Authenticate interactively via OAuth 2.0 (desktop flow)."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds: Credentials | None = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"OAuth credentials not found: {credentials_path}\n"
                    "Download from Google Cloud Console → Credentials → OAuth 2.0 Client ID."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json(), encoding="utf-8")
        log.info("Token saved to %s", token_path)

    return creds


def upload_or_update(
    creds: Credentials,
    content: str,
    filename: str,
    file_id: str | None = None,
    folder_id: str | None = None,
) -> str:
    """Upload content as a text file to Google Drive.

    If file_id is provided, updates the existing file (idempotent link).
    If file_id is None, creates a new file and returns its ID.
    """
    service = build("drive", "v3", credentials=creds)

    media = MediaInMemoryUpload(
        content.encode("utf-8"),
        mimetype="text/plain",
        resumable=False,
    )

    if file_id:
        # Update existing file
        result = (
            service.files()
            .update(fileId=file_id, media_body=media)
            .execute()
        )
        log.info("Updated Drive file: %s", file_id)
        return str(result["id"])
    else:
        # Create new file
        metadata: dict[str, Any] = {"name": filename}
        if folder_id:
            metadata["parents"] = [folder_id]

        result = (
            service.files()
            .create(body=metadata, media_body=media, fields="id")
            .execute()
        )
        new_id = str(result["id"])
        log.info("Created Drive file: %s (id: %s)", filename, new_id)
        return new_id

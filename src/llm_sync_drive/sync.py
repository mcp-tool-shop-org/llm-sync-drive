"""Core sync logic — shared between CLI and MCP server."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import yaml

from .compiler import compile_llms_txt
from .config import Config, CONFIG_FILENAME
from .drive import authenticate, upload_or_update

log = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of a compile + upload cycle."""

    file_id: str
    bytes_compiled: int
    files_included: int
    drive_filename: str
    repo_path: str
    local_output: str | None = None


def do_sync(config: Config, config_path: Path | None = None) -> SyncResult:
    """Compile the repo into llms.txt and upload to Google Drive.

    Returns a SyncResult with metadata about what happened.
    """
    log.info("Compiling llms.txt from %s", config.repo_path)
    content = compile_llms_txt(config)

    # Count files from the compiled output header
    files_included = content.count("\n### ") 
    log.info("Compiled %d bytes (%d files)", len(content), files_included)

    # Write local copy if configured
    local_path: str | None = None
    if config.local_output:
        config.local_output.parent.mkdir(parents=True, exist_ok=True)
        config.local_output.write_text(content, encoding="utf-8")
        local_path = str(config.local_output)
        log.info("Local copy written to %s", config.local_output)

    # Upload to Drive
    creds = authenticate(config.credentials_path, config.token_path, config.auth_mode)
    file_id = upload_or_update(
        creds=creds,
        content=content,
        filename=config.drive_filename,
        file_id=config.drive_file_id,
        folder_id=config.drive_folder_id,
    )

    # Save file_id back to config if this was the first upload
    if config.drive_file_id is None:
        _save_file_id(file_id, config_path)
        config.drive_file_id = file_id
        log.info("Drive file ID saved to config: %s", file_id)

    log.info("Sync complete — Drive file: %s", file_id)

    return SyncResult(
        file_id=file_id,
        bytes_compiled=len(content),
        files_included=files_included,
        drive_filename=config.drive_filename,
        repo_path=str(config.repo_path),
        local_output=local_path,
    )


def _save_file_id(file_id: str, config_path: Path | None = None) -> None:
    """Write the drive_file_id back into the config YAML."""
    if config_path is None:
        config_path = Path.cwd() / CONFIG_FILENAME
    if not config_path.exists():
        return

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return

    raw["drive_file_id"] = file_id

    config_path.write_text(
        yaml.dump(raw, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

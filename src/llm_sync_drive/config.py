"""Configuration loading and defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Config:
    """Runtime configuration for llm-sync-drive."""

    # Path to the repository to compile
    repo_path: Path

    # Google Drive file ID to update (set after first upload)
    drive_file_id: str | None = None

    # Google Drive folder ID to upload into (used on first upload)
    drive_folder_id: str | None = None

    # Path to Google OAuth credentials JSON
    credentials_path: Path = Path("credentials.json")

    # Path to cached token
    token_path: Path = Path("token.json")

    # Output filename in Drive
    drive_filename: str = "llms.txt"

    # Local output path (optional, for inspection)
    local_output: Path | None = None

    # Debounce interval in seconds for the file watcher
    debounce_seconds: float = 5.0

    # Max file size in bytes before skipping a file (default 100KB)
    max_file_bytes: int = 100_000

    # File extensions to include (empty = all text files)
    include_extensions: list[str] = field(default_factory=list)

    # Extra ignore patterns beyond .gitignore / .llmsignore
    extra_ignore_patterns: list[str] = field(default_factory=list)

    # Project description for the llms.txt header
    project_description: str = ""


CONFIG_FILENAME = "llm-sync-drive.yaml"


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = Path.cwd() / CONFIG_FILENAME

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Run 'llm-sync-drive init' to create one."
        )

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Config file must be a YAML mapping: {config_path}")

    return _parse_config(raw, config_path.parent)


def _parse_config(data: dict[str, Any], base_dir: Path) -> Config:
    """Parse raw YAML dict into Config, resolving paths relative to base_dir."""
    repo_path = data.get("repo_path")
    if not repo_path:
        raise ValueError("'repo_path' is required in config")

    repo = Path(repo_path)
    if not repo.is_absolute():
        repo = (base_dir / repo).resolve()

    cfg = Config(repo_path=repo)

    if v := data.get("drive_file_id"):
        cfg.drive_file_id = str(v)
    if v := data.get("drive_folder_id"):
        cfg.drive_folder_id = str(v)
    if v := data.get("credentials_path"):
        p = Path(v)
        cfg.credentials_path = p if p.is_absolute() else (base_dir / p).resolve()
    if v := data.get("token_path"):
        p = Path(v)
        cfg.token_path = p if p.is_absolute() else (base_dir / p).resolve()
    if v := data.get("drive_filename"):
        cfg.drive_filename = str(v)
    if v := data.get("local_output"):
        p = Path(v)
        cfg.local_output = p if p.is_absolute() else (base_dir / p).resolve()
    if v := data.get("debounce_seconds"):
        cfg.debounce_seconds = float(v)
    if v := data.get("max_file_bytes"):
        cfg.max_file_bytes = int(v)
    if v := data.get("include_extensions"):
        cfg.include_extensions = [str(e) for e in v]
    if v := data.get("extra_ignore_patterns"):
        cfg.extra_ignore_patterns = [str(p) for p in v]
    if v := data.get("project_description"):
        cfg.project_description = str(v)

    return cfg


def generate_default_config(repo_path: str = ".") -> str:
    """Generate a default YAML config string."""
    return f"""\
# llm-sync-drive configuration
# See README.md for full documentation

# Path to the repository to compile (relative to this file, or absolute)
repo_path: "{repo_path}"

# Google OAuth credentials file (download from Google Cloud Console)
credentials_path: "credentials.json"

# Cached OAuth token (created automatically after first auth)
token_path: "token.json"

# Google Drive folder ID to upload into (from the Drive URL)
# drive_folder_id: "1ABCdefGHIjklMNOpqrSTUvwxYZ"

# Google Drive file ID (set automatically after first upload — do not edit)
# drive_file_id: null

# Filename in Google Drive
drive_filename: "llms.txt"

# Also write to a local file for inspection
# local_output: "llms.txt"

# Description shown at the top of the compiled llms.txt
project_description: ""

# Debounce interval: wait this many seconds after last change before syncing
debounce_seconds: 5.0

# Skip files larger than this (bytes). Default 100KB.
max_file_bytes: 100000

# Only include these extensions (empty = all detected text files)
# include_extensions:
#   - .py
#   - .ts
#   - .md

# Extra ignore patterns (in addition to .gitignore and .llmsignore)
# extra_ignore_patterns:
#   - "*.log"
#   - "dist/"
"""

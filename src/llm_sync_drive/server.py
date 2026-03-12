"""MCP server for llm-sync-drive — exposes sync tools to AI assistants."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .compiler import compile_llms_txt
from .config import Config, load_config, CONFIG_FILENAME
from .sync import do_sync

log = logging.getLogger(__name__)

mcp = FastMCP(
    "llm-sync-drive",
    instructions="Compile repository context into llms.txt and sync to Google Drive",
)


def _resolve_config(repo_path: str | None = None, config_path: str | None = None) -> tuple[Config, Path | None]:
    """Resolve config: explicit config file, or build one from repo_path + env vars."""
    # If explicit config file given, use it
    if config_path:
        cp = Path(config_path)
        return load_config(cp), cp

    # Check env var for default config location
    env_config = os.environ.get("LLM_SYNC_DRIVE_CONFIG")
    if env_config:
        cp = Path(env_config)
        if cp.exists():
            cfg = load_config(cp)
            # Override repo_path if caller specified one
            if repo_path:
                cfg.repo_path = Path(repo_path).resolve()
            return cfg, cp

    # If repo_path given, try to find config in that directory
    if repo_path:
        rp = Path(repo_path).resolve()
        candidate = rp / CONFIG_FILENAME
        if candidate.exists():
            cfg = load_config(candidate)
            return cfg, candidate

        # No config file — build a minimal Config from env vars
        cfg = Config(repo_path=rp)

        # Pull Drive settings from env
        if v := os.environ.get("LLM_SYNC_DRIVE_FILE_ID"):
            cfg.drive_file_id = v
        if v := os.environ.get("LLM_SYNC_DRIVE_FOLDER_ID"):
            cfg.drive_folder_id = v
        if v := os.environ.get("LLM_SYNC_DRIVE_CREDENTIALS"):
            cfg.credentials_path = Path(v)
        if v := os.environ.get("LLM_SYNC_DRIVE_TOKEN"):
            cfg.token_path = Path(v)

        return cfg, None

    # Fall back to CWD config
    return load_config(), Path.cwd() / CONFIG_FILENAME


@mcp.tool()
def sync_to_drive(
    repo_path: str | None = None,
    config_path: str | None = None,
    message: str = "",
) -> str:
    """Compile a repository into llms.txt and upload to Google Drive.

    Use after completing a phase, milestone, or significant change.
    The Drive file is updated in-place so the link stays permanent.

    Args:
        repo_path: Path to the repository to compile. Defaults to config or CWD.
        config_path: Path to llm-sync-drive.yaml config file. Optional.
        message: Optional note about what changed (logged, not uploaded).
    """
    try:
        cfg, cp = _resolve_config(repo_path, config_path)
        if message:
            log.info("Sync reason: %s", message)
        result = do_sync(cfg, cp)
        return (
            f"Synced to Google Drive successfully.\n"
            f"  Repository: {result.repo_path}\n"
            f"  Files included: {result.files_included}\n"
            f"  Size: {result.bytes_compiled:,} bytes\n"
            f"  Drive file ID: {result.file_id}\n"
            f"  Drive filename: {result.drive_filename}"
        )
    except Exception as e:
        return f"Sync failed: {e}"


@mcp.tool()
def compile_context(
    repo_path: str | None = None,
    config_path: str | None = None,
    save_to: str | None = None,
) -> str:
    """Compile a repository into llms.txt format WITHOUT uploading.

    Useful for previewing what would be synced, or saving a local snapshot.

    Args:
        repo_path: Path to the repository to compile. Defaults to config or CWD.
        config_path: Path to llm-sync-drive.yaml config file. Optional.
        save_to: If provided, write the compiled output to this local file path.
    """
    try:
        cfg, _ = _resolve_config(repo_path, config_path)
        content = compile_llms_txt(cfg)
        file_count = content.count("\n### ")

        if save_to:
            out = Path(save_to)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(content, encoding="utf-8")
            return (
                f"Compiled and saved to {out}\n"
                f"  Repository: {cfg.repo_path}\n"
                f"  Files included: {file_count}\n"
                f"  Size: {len(content):,} bytes"
            )
        else:
            return (
                f"Compiled successfully (not uploaded).\n"
                f"  Repository: {cfg.repo_path}\n"
                f"  Files included: {file_count}\n"
                f"  Size: {len(content):,} bytes\n\n"
                f"--- BEGIN llms.txt ---\n{content}\n--- END llms.txt ---"
            )
    except Exception as e:
        return f"Compile failed: {e}"


@mcp.tool()
def sync_status(
    config_path: str | None = None,
) -> str:
    """Check the current sync configuration and Drive file status.

    Args:
        config_path: Path to llm-sync-drive.yaml config file. Optional.
    """
    try:
        cfg, cp = _resolve_config(config_path=config_path)
        lines = [
            "llm-sync-drive status:",
            f"  Config: {cp or 'env vars / defaults'}",
            f"  Repository: {cfg.repo_path}",
            f"  Repo exists: {cfg.repo_path.is_dir()}",
            f"  Drive file ID: {cfg.drive_file_id or '(not yet uploaded)'}",
            f"  Drive folder ID: {cfg.drive_folder_id or '(not set)'}",
            f"  Drive filename: {cfg.drive_filename}",
            f"  Credentials: {cfg.credentials_path} (exists: {cfg.credentials_path.exists()})",
            f"  Token: {cfg.token_path} (exists: {cfg.token_path.exists()})",
            f"  Max file size: {cfg.max_file_bytes:,} bytes",
            f"  Debounce: {cfg.debounce_seconds}s",
        ]
        if cfg.include_extensions:
            lines.append(f"  Include extensions: {', '.join(cfg.include_extensions)}")
        if cfg.extra_ignore_patterns:
            lines.append(f"  Extra ignores: {', '.join(cfg.extra_ignore_patterns)}")
        return "\n".join(lines)
    except Exception as e:
        return f"Status check failed: {e}"


@mcp.tool()
def list_repos(
    search_dir: str = "F:\\AI",
) -> str:
    """List repositories that have llm-sync-drive.yaml configs.

    Scans a directory for repos with existing sync configurations.

    Args:
        search_dir: Directory to search for configured repos.
    """
    try:
        base = Path(search_dir).resolve()
        if not base.is_dir():
            return f"Directory not found: {base}"

        found: list[str] = []
        for config_file in base.rglob(CONFIG_FILENAME):
            # Don't recurse too deep
            if len(config_file.relative_to(base).parts) > 3:
                continue
            try:
                cfg = load_config(config_file)
                status = "linked" if cfg.drive_file_id else "not uploaded"
                found.append(f"  {config_file.parent} [{status}]")
            except Exception:
                found.append(f"  {config_file.parent} [config error]")

        if not found:
            return f"No llm-sync-drive configs found under {base}"
        return f"Configured repos under {base}:\n" + "\n".join(found)
    except Exception as e:
        return f"Search failed: {e}"


def main() -> None:
    """Run the MCP server via stdio transport."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

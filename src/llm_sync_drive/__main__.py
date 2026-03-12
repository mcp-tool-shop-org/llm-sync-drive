"""CLI entry point for llm-sync-drive."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

from .compiler import compile_llms_txt
from .config import generate_default_config, load_config, CONFIG_FILENAME
from .sync import do_sync
from .watcher import watch

log = logging.getLogger("llm_sync_drive")


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging")
def cli(verbose: bool) -> None:
    """llm-sync-drive — Compile llms.txt and sync to Google Drive."""
    _setup_logging(verbose)


@cli.command()
@click.option(
    "--repo", "-r",
    type=click.Path(exists=True, file_okay=False),
    default=".",
    help="Repository path (default: current directory)",
)
def init(repo: str) -> None:
    """Create a default configuration file."""
    config_path = Path.cwd() / CONFIG_FILENAME
    if config_path.exists():
        click.echo(f"Config already exists: {config_path}")
        sys.exit(1)

    content = generate_default_config(repo)
    config_path.write_text(content, encoding="utf-8")
    click.echo(f"Created {config_path}")
    click.echo("Edit it to set your credentials_path and drive_folder_id, then run:")
    click.echo("  llm-sync-drive sync")


@cli.command()
@click.option(
    "--config", "-c", "config_path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help=f"Config file (default: ./{CONFIG_FILENAME})",
)
def sync(config_path: str | None) -> None:
    """Compile llms.txt and upload to Google Drive (one-shot)."""
    p = Path(config_path) if config_path else None
    cfg = load_config(p)
    result = do_sync(cfg, p)
    click.echo(f"Synced {result.bytes_compiled} bytes → {result.file_id}")


@cli.command()
@click.option(
    "--config", "-c", "config_path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help=f"Config file (default: ./{CONFIG_FILENAME})",
)
def serve(config_path: str | None) -> None:
    """Watch the repo and auto-sync on changes."""
    p = Path(config_path) if config_path else None
    cfg = load_config(p)

    # Initial sync
    do_sync(cfg, p)

    # Watch for changes
    click.echo(f"Watching {cfg.repo_path} — press Ctrl+C to stop")
    watch(cfg.repo_path, lambda: do_sync(cfg, p), cfg.debounce_seconds)


@cli.command()
@click.option(
    "--config", "-c", "config_path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help=f"Config file (default: ./{CONFIG_FILENAME})",
)
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False),
    default=None,
    help="Output file (default: stdout)",
)
def compile(config_path: str | None, output: str | None) -> None:
    """Compile llms.txt locally without uploading."""
    cfg = load_config(Path(config_path) if config_path else None)
    content = compile_llms_txt(cfg)

    if output:
        out = Path(output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        click.echo(f"Written to {out} ({len(content)} bytes)")
    else:
        click.echo(content)


@cli.command()
def auth() -> None:
    """Authenticate with Google Drive (interactive)."""
    from .drive import authenticate

    cfg = load_config()
    creds = authenticate(cfg.credentials_path, cfg.token_path, auth_mode="oauth")
    click.echo(f"Authenticated successfully. Token saved to {cfg.token_path}")


if __name__ == "__main__":
    cli()

"""Ignore-file parser — combines .gitignore and .llmsignore rules."""

from __future__ import annotations

from pathlib import Path

import pathspec


# Patterns always ignored regardless of config
BUILTIN_IGNORES = [
    ".git/",
    ".git/**",
    "node_modules/",
    "node_modules/**",
    "__pycache__/",
    "__pycache__/**",
    "*.pyc",
    ".env",
    ".env.*",
    "*.secret",
    "*.key",
    "*.pem",
    "*.p12",
    "*.pfx",
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
]


def load_ignore_spec(repo_path: Path, extra_patterns: list[str] | None = None) -> pathspec.PathSpec:
    """Build a combined PathSpec from .gitignore, .llmsignore, builtins, and extras."""
    patterns: list[str] = list(BUILTIN_IGNORES)

    for ignore_file in (".gitignore", ".llmsignore"):
        p = repo_path / ignore_file
        if p.is_file():
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    patterns.append(stripped)

    if extra_patterns:
        patterns.extend(extra_patterns)

    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

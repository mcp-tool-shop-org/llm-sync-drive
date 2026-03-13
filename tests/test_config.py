"""Tests for config parsing and generation."""

from pathlib import Path

import pytest

from llm_sync_drive.config import _parse_config, generate_default_config, load_config


class TestParseConfig:
    def test_minimal(self, tmp_path):
        cfg = _parse_config({"repo_path": str(tmp_path)}, tmp_path)
        assert cfg.repo_path == tmp_path
        assert cfg.auth_mode == "adc"
        assert cfg.drive_file_id is None
        assert cfg.max_file_bytes == 100_000

    def test_relative_repo_path(self, tmp_path):
        cfg = _parse_config({"repo_path": "subdir"}, tmp_path)
        assert cfg.repo_path == (tmp_path / "subdir").resolve()

    def test_absolute_repo_path(self, tmp_path):
        abs_path = str(tmp_path / "myrepo")
        cfg = _parse_config({"repo_path": abs_path}, tmp_path)
        assert cfg.repo_path == Path(abs_path)

    def test_all_fields(self, tmp_path):
        data = {
            "repo_path": str(tmp_path),
            "drive_file_id": "abc123",
            "drive_folder_id": "folder456",
            "credentials_path": "creds.json",
            "token_path": "tok.json",
            "auth_mode": "service-account",
            "drive_filename": "context.txt",
            "local_output": "out.txt",
            "debounce_seconds": 10.0,
            "max_file_bytes": 50_000,
            "include_extensions": [".py", ".md"],
            "extra_ignore_patterns": ["*.log"],
            "project_description": "My project",
        }
        cfg = _parse_config(data, tmp_path)
        assert cfg.drive_file_id == "abc123"
        assert cfg.drive_folder_id == "folder456"
        assert cfg.credentials_path == (tmp_path / "creds.json").resolve()
        assert cfg.auth_mode == "service-account"
        assert cfg.drive_filename == "context.txt"
        assert cfg.local_output == (tmp_path / "out.txt").resolve()
        assert cfg.debounce_seconds == 10.0
        assert cfg.max_file_bytes == 50_000
        assert cfg.include_extensions == [".py", ".md"]
        assert cfg.extra_ignore_patterns == ["*.log"]
        assert cfg.project_description == "My project"

    def test_missing_repo_path_raises(self, tmp_path):
        with pytest.raises(ValueError, match="repo_path"):
            _parse_config({}, tmp_path)


class TestLoadConfig:
    def test_load_valid_yaml(self, tmp_path):
        cfg_file = tmp_path / "llm-sync-drive.yaml"
        # Use forward slashes to avoid YAML escape issues on Windows
        repo_str = str(tmp_path).replace("\\", "/")
        cfg_file.write_text(f'repo_path: "{repo_str}"\nauth_mode: "adc"\n')
        cfg = load_config(cfg_file)
        assert cfg.repo_path == Path(repo_str)
        assert cfg.auth_mode == "adc"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_config(tmp_path / "nonexistent.yaml")

    def test_invalid_yaml_raises(self, tmp_path):
        cfg_file = tmp_path / "llm-sync-drive.yaml"
        cfg_file.write_text("just a string")
        with pytest.raises(ValueError, match="YAML mapping"):
            load_config(cfg_file)


class TestGenerateDefaultConfig:
    def test_contains_repo_path(self):
        output = generate_default_config("/my/repo")
        assert 'repo_path: "/my/repo"' in output

    def test_contains_adc_default(self):
        output = generate_default_config()
        assert 'auth_mode: "adc"' in output

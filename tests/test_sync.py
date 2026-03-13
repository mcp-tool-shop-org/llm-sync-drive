"""Tests for sync orchestration (mocked Drive API)."""

from unittest.mock import MagicMock, patch

import yaml

from llm_sync_drive.config import Config
from llm_sync_drive.sync import SyncResult, _save_file_id, do_sync


class TestDoSync:
    def _make_repo(self, tmp_path):
        (tmp_path / "main.py").write_text("x = 1\n")
        return tmp_path

    @patch("llm_sync_drive.sync.upload_or_update", return_value="file-abc")
    @patch("llm_sync_drive.sync.authenticate", return_value=MagicMock())
    def test_returns_sync_result(self, mock_auth, mock_upload, tmp_path):
        repo = self._make_repo(tmp_path)
        cfg = Config(repo_path=repo)
        result = do_sync(cfg)
        assert isinstance(result, SyncResult)
        assert result.file_id == "file-abc"
        assert result.bytes_compiled > 0
        assert result.drive_filename == "llms.txt"

    @patch("llm_sync_drive.sync.upload_or_update", return_value="file-abc")
    @patch("llm_sync_drive.sync.authenticate", return_value=MagicMock())
    def test_writes_local_output(self, mock_auth, mock_upload, tmp_path):
        repo = self._make_repo(tmp_path)
        local_out = tmp_path / "output" / "llms.txt"
        cfg = Config(repo_path=repo, local_output=local_out)
        result = do_sync(cfg)
        assert local_out.exists()
        assert result.local_output == str(local_out)

    @patch("llm_sync_drive.sync.upload_or_update", return_value="new-id")
    @patch("llm_sync_drive.sync.authenticate", return_value=MagicMock())
    def test_saves_file_id_on_first_upload(self, mock_auth, mock_upload, tmp_path):
        repo = self._make_repo(tmp_path)
        cfg_file = tmp_path / "llm-sync-drive.yaml"
        cfg_file.write_text(yaml.dump({"repo_path": str(repo)}))
        cfg = Config(repo_path=repo)
        do_sync(cfg, config_path=cfg_file)
        raw = yaml.safe_load(cfg_file.read_text())
        assert raw["drive_file_id"] == "new-id"

    @patch("llm_sync_drive.sync.upload_or_update", return_value="existing-id")
    @patch("llm_sync_drive.sync.authenticate", return_value=MagicMock())
    def test_skips_save_when_file_id_exists(self, mock_auth, mock_upload, tmp_path):
        repo = self._make_repo(tmp_path)
        cfg_file = tmp_path / "llm-sync-drive.yaml"
        cfg_file.write_text(yaml.dump({"repo_path": str(repo), "drive_file_id": "existing-id"}))
        cfg = Config(repo_path=repo, drive_file_id="existing-id")
        do_sync(cfg, config_path=cfg_file)
        raw = yaml.safe_load(cfg_file.read_text())
        assert raw["drive_file_id"] == "existing-id"


class TestSaveFileId:
    def test_writes_id_to_yaml(self, tmp_path):
        cfg_file = tmp_path / "llm-sync-drive.yaml"
        cfg_file.write_text(yaml.dump({"repo_path": "."}))
        _save_file_id("new-id-123", cfg_file)
        raw = yaml.safe_load(cfg_file.read_text())
        assert raw["drive_file_id"] == "new-id-123"

    def test_noop_when_no_config(self, tmp_path):
        _save_file_id("id", tmp_path / "nonexistent.yaml")

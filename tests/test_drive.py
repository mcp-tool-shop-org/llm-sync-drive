"""Tests for Google Drive API integration (fully mocked)."""

from pathlib import Path
from unittest.mock import MagicMock, patch


from llm_sync_drive.drive import authenticate, upload_or_update


class TestAuthenticate:
    @patch("llm_sync_drive.drive._auth_adc")
    def test_adc_mode(self, mock_adc):
        mock_adc.return_value = MagicMock()
        creds = authenticate(Path("c.json"), Path("t.json"), auth_mode="adc")
        mock_adc.assert_called_once()
        assert creds is not None

    @patch("llm_sync_drive.drive._auth_service_account")
    def test_service_account_mode(self, mock_sa):
        mock_sa.return_value = MagicMock()
        authenticate(Path("c.json"), Path("t.json"), auth_mode="service-account")
        mock_sa.assert_called_once_with(Path("c.json"))

    @patch("llm_sync_drive.drive._auth_oauth")
    def test_oauth_mode(self, mock_oauth):
        mock_oauth.return_value = MagicMock()
        authenticate(Path("c.json"), Path("t.json"), auth_mode="oauth")
        mock_oauth.assert_called_once_with(Path("c.json"), Path("t.json"))


class TestUploadOrUpdate:
    @patch("llm_sync_drive.drive.build")
    def test_update_existing_file(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.files().update().execute.return_value = {"id": "existing-id"}

        result = upload_or_update(MagicMock(), "content", "llms.txt", file_id="existing-id")
        assert result == "existing-id"

    @patch("llm_sync_drive.drive.build")
    def test_create_new_file(self, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.files().create().execute.return_value = {"id": "new-id"}

        result = upload_or_update(MagicMock(), "content", "llms.txt", file_id=None, folder_id="folder-1")
        assert result == "new-id"

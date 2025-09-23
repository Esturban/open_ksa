# tests/test_get_dataset_resource.py
import unittest
from unittest.mock import patch, MagicMock
from open_ksa.get_dataset_resource import (
    get_dataset_resource,
)  # Adjust the import based on your package structure
import os


class TestGetDatasetResource(unittest.TestCase):

    @patch("open_ksa.get_dataset_resource.SingletonSession.get_instance")
    @patch("open_ksa.get_dataset_resource.download_file")
    @patch("os.makedirs")
    @patch("os.path.exists")
    @patch("os.path.getsize")
    @patch("os.remove")
    def test_get_dataset_resource_successful_download(
        self,
        mock_remove,
        mock_getsize,
        mock_exists,
        mock_makedirs,
        mock_download_file,
        mock_session_get_instance,
    ):
        # Setup mocks
        mock_session = MagicMock()
        mock_session_get_instance.return_value = mock_session

        # Mock dataset response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "resources": [
                {
                    "downloadUrl": "https://example.com/file.csv",
                    "id": "resource_id_1",
                }
            ],
            "datasetId": "dataset_id_1",
        }
        mock_session.get.return_value = mock_response

        # Mock os.path.exists and os.path.getsize
        mock_exists.return_value = False
        mock_getsize.return_value = 0

        # Mock download_file to return a file size
        mock_download_file.return_value = 1024  # Assume 1KB file size

        # Call the function
        get_dataset_resource("dataset_id_1", verbose=True)

        # Assertions for the initial API call to get dataset resources
        mock_session.get.assert_called_with(
            "https://open.data.gov.sa/data/api/datasets/resources",
            params={"version": "-1", "dataset": "dataset_id_1"},
            headers={
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                "Referer": "https://open.data.gov.sa/",
                "Accept-Language": "en-US,en;q=0.9",
                "Host": "open.data.gov.sa",
                "Upgrade-Insecure-Requests": "1",
            },
        )

        # Assertions for the download process
        mock_makedirs.assert_called_once_with("opendata/org_resources", exist_ok=True)
        mock_download_file.assert_called_once_with(
            mock_session,
            "https://open.data.gov.sa/data/api/v1/datasets/dataset_id_1/resources/resource_id_1/download",
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                "Referer": "https://open.data.gov.sa/en/datasets/view/dataset_id_1/resources",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.9",
                "Host": "open.data.gov.sa",
                "Upgrade-Insecure-Requests": "1",
                "X-Requested-With": "XMLHttpRequest",
                "Connection": "keep-alive",
            },
            "opendata/org_resources/file.csv",
        )


if __name__ == "__main__":
    unittest.main()

from unittest.mock import patch


@patch("open_ksa.manifest.write_manifest")
@patch("open_ksa.downloader.fetch_and_load")
def test_cli_download_flow(mock_fetch_and_load, mock_write_manifest):
    # Arrange: simulate fetch_and_load returning the canonical manifest object and data_map
    from open_ksa.models import DownloadManifest, SelectionRequest

    manifest = DownloadManifest(
        manifest_id="m-1",
        requested_scope=SelectionRequest(scope_type="dataset", dataset_ids=["dataset_1"]),
        requested_at="2026-03-10T00:00:00+00:00",
        dest_path="/tmp",
        entries=[],
    )
    data_map = {}
    mock_fetch_and_load.return_value = (manifest, data_map)

    # Import CLI and run download_cli
    import importlib
    cli = importlib.import_module("open_ksa.cli")

    # Execute
    manifest_out = cli.download_cli(dataset_id="dataset_1", dest="/tmp", sample_size=10)
    # Assert fetch_and_load was called and write_manifest was invoked
    mock_fetch_and_load.assert_called_once()
    mock_write_manifest.assert_called_once_with(manifest, "/tmp/manifest.json")
    assert manifest_out is manifest

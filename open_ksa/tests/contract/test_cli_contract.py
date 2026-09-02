from unittest.mock import patch

import pytest


def test_cli_contract_exists():
    import importlib
    cli = importlib.import_module("open_ksa.cli")
    assert hasattr(cli, "browse_cli")
    assert hasattr(cli, "download_cli")
    assert hasattr(cli, "main")


def test_download_cli_returns_manifest():
    import importlib
    cli = importlib.import_module("open_ksa.cli")
    models = importlib.import_module("open_ksa.models")
    manifest = cli.download_cli(dest=".", interactive=False)
    assert isinstance(manifest, models.DownloadManifest)
    assert hasattr(manifest, "entries")


def test_download_cli_propagates_downloader_failure_instead_of_faking_a_manifest():
    """A real failure in fetch_and_load must surface as an exception, not get
    papered over with a synthetic manifest containing a fake resource_id."""
    import importlib
    cli = importlib.import_module("open_ksa.cli")

    with patch("open_ksa.cli.downloader.fetch_and_load", side_effect=RuntimeError("boom")):
        with pytest.raises(RuntimeError, match="boom"):
            cli.download_cli(dest=".", interactive=False)


def test_browse_cli_wires_organization_and_dataset_selection():
    """browse_cli must not raise NotImplementedError: it walks organization ->
    dataset -> download using the existing notebook browse helpers."""
    import importlib
    cli = importlib.import_module("open_ksa.cli")

    with patch("open_ksa.cli.notebook.browse_organizations", return_value="org-1") as mock_orgs, \
         patch("open_ksa.cli.notebook.browse_datasets", return_value="ds-1") as mock_datasets, \
         patch("open_ksa.cli.download_cli", return_value="manifest-stub") as mock_download:
        result = cli.browse_cli(query="water")

    mock_orgs.assert_called_once_with(query="water", interactive=True)
    mock_datasets.assert_called_once_with("org-1", interactive=True)
    mock_download.assert_called_once_with(dataset_id="ds-1", organization_id="org-1", dest=".")
    assert result == "manifest-stub"


def test_browse_cli_returns_none_when_no_organization_chosen():
    import importlib
    cli = importlib.import_module("open_ksa.cli")
    with patch("open_ksa.cli.notebook.browse_organizations", return_value=None):
        assert cli.browse_cli() is None


def test_browse_cli_returns_none_when_no_dataset_chosen():
    import importlib
    cli = importlib.import_module("open_ksa.cli")
    with patch("open_ksa.cli.notebook.browse_organizations", return_value="org-1"), \
         patch("open_ksa.cli.notebook.browse_datasets", return_value=None):
        assert cli.browse_cli() is None

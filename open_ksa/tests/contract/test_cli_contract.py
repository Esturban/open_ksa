import pytest


def test_cli_contract_exists():
    import importlib
    cli = importlib.import_module("open_ksa.cli")
    assert hasattr(cli, "browse_cli")
    assert hasattr(cli, "download_cli")


def test_cli_raises_not_implemented():
    import importlib
    cli = importlib.import_module("open_ksa.cli")
    models = importlib.import_module("open_ksa.models")
    with pytest.raises(NotImplementedError):
        cli.browse_cli()
    # download_cli should expose the canonical manifest object
    manifest = cli.download_cli(dest=".", interactive=False)
    assert isinstance(manifest, models.DownloadManifest)
    assert hasattr(manifest, "entries")

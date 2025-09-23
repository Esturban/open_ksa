import pytest


def test_cli_contract_exists():
    import importlib
    cli = importlib.import_module("open_ksa.cli")
    assert hasattr(cli, "browse_cli")
    assert hasattr(cli, "download_cli")


def test_cli_raises_not_implemented():
    import importlib
    cli = importlib.import_module("open_ksa.cli")
    with pytest.raises(NotImplementedError):
        cli.browse_cli()
    # download_cli now provides a safe demo manifest fallback; ensure it returns a manifest dict
    manifest = cli.download_cli(dest=".", interactive=False)
    assert isinstance(manifest, dict)
    assert "entries" in manifest

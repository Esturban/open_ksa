import pytest


def test_browse_contract_exists():
    import importlib

    downloader = importlib.import_module("open_ksa.downloader")
    assert hasattr(downloader, "browse")


def test_browse_raises_not_implemented():
    import importlib

    downloader = importlib.import_module("open_ksa.downloader")
    with pytest.raises(NotImplementedError):
        downloader.browse()

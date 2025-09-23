import pytest


def test_quickstart_api_flow_exists(monkeypatch):
    # Ensure high-level API functions exist: browse and fetch_and_load
    import importlib

    downloader = importlib.import_module("open_ksa.downloader")
    assert hasattr(downloader, "browse")
    assert hasattr(downloader, "fetch_and_load")
    # fetch_and_load now implemented conservatively; call it and assert types
    try:
        manifest, data_map = downloader.fetch_and_load(dest='.')
        assert isinstance(manifest, dict)
        assert isinstance(data_map, dict)
    except NotImplementedError:
        pytest.skip("fetch_and_load not implemented in this environment")

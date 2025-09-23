import pytest


def test_fetch_and_load_contract_exists():
    """Contract test: `open_ksa.downloader.fetch_and_load` should exist as the public API.

    This test is intentionally written before implementation and is expected to fail
    until the downloader module and function are implemented.
    """
    import importlib

    # Attempt to import the downloader module and access the API symbol.
    # If the module or symbol is missing, this test will fail, satisfying TDD.
    downloader = importlib.import_module("open_ksa.downloader")
    assert hasattr(downloader, "fetch_and_load")


def test_fetch_and_load_raises_not_implemented():
    import importlib

    downloader = importlib.import_module("open_ksa.downloader")
    # fetch_and_load now has a working conservative implementation; assert it returns manifest,data_map
    manifest, data_map = downloader.fetch_and_load(dataset_id="nonexistent", dest=".")
    assert isinstance(manifest, dict)
    assert isinstance(data_map, dict)

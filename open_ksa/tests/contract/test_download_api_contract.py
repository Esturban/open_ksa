

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


def test_fetch_and_load_returns_manifest_object():
    import importlib

    downloader = importlib.import_module("open_ksa.downloader")
    models = importlib.import_module("open_ksa.models")

    manifest, data_map = downloader.fetch_and_load(
        selection={
            "scope_type": "dataset",
            "dataset_ids": [],
            "organization_ids": [],
            "resource_ids": [],
        },
        dest=".",
    )
    assert isinstance(manifest, models.DownloadManifest)
    assert isinstance(data_map, dict)
    assert hasattr(manifest, "entries")
    assert hasattr(manifest, "completeness_summary")

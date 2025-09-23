import pytest


def test_streaming_sample_interface_exists():
    import importlib

    downloader = importlib.import_module("open_ksa.downloader")
    assert hasattr(downloader, "sample_and_load") or hasattr(
        downloader, "fetch_and_load"
    )
    # calling without implementation should raise NotImplementedError
    with pytest.raises(NotImplementedError):
        if hasattr(downloader, "sample_and_load"):
            downloader.sample_and_load(10)
        else:
            downloader.fetch_and_load(sample_size=10)

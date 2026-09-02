import pytest


def test_on_disk_prompt_behavior_exists(monkeypatch):
    import importlib

    downloader = importlib.import_module("open_ksa.downloader")
    # Expect on-disk logic to exist; calling it without implementation raises NotImplementedError
    assert hasattr(downloader, "fetch_and_load")
    with pytest.raises(NotImplementedError):
        downloader.fetch_and_load(on_disk_threshold_bytes=1)

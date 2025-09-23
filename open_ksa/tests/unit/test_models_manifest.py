import pytest


def test_manifest_model_fields_exist():
    import importlib

    models = importlib.import_module("open_ksa.models")
    assert hasattr(models, "DownloadManifest")
    mf_cls = getattr(models, "DownloadManifest")
    for field in ("timestamp", "requested_by", "dest_path", "entries"):
        assert hasattr(mf_cls, field) or field in getattr(
            mf_cls, "__annotations__", {}
        ), f"Missing field {field}"

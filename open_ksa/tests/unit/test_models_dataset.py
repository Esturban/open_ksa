import pytest


def test_dataset_model_fields_exist():
    import importlib

    models = importlib.import_module("open_ksa.models")
    assert hasattr(models, "Dataset")
    ds_cls = getattr(models, "Dataset")
    for field in ("dataset_id", "title", "resources"):
        assert hasattr(ds_cls, field) or field in getattr(
            ds_cls, "__annotations__", {}
        ), f"Missing field {field}"

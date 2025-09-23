import pytest


def test_resource_model_fields_exist():
    import importlib

    models = importlib.import_module("open_ksa.models")
    assert hasattr(models, "Resource")
    res_cls = getattr(models, "Resource")
    for field in ("resource_id", "name", "url", "format", "content_type", "size"):
        assert hasattr(res_cls, field) or field in getattr(
            res_cls, "__annotations__", {}
        ), f"Missing field {field}"

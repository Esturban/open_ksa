import pytest


def test_organization_model_fields_exist():
    import importlib

    models = importlib.import_module("open_ksa.models")
    assert hasattr(models, "Organization")
    org_cls = getattr(models, "Organization")
    # Expect dataclass or class with attributes; test presence of common fields
    for field in ("organization_id", "title", "description", "dataset_count"):
        assert hasattr(org_cls, field) or field in getattr(
            org_cls, "__annotations__", {}
        ), f"Missing field {field}"

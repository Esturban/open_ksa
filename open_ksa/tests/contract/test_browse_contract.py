import pytest


def test_browse_organizations_contract_exists():
    import importlib
    nb = importlib.import_module("open_ksa.notebook")
    assert hasattr(nb, "browse_organizations")
    # call non-interactive: expect a list (may be empty) or None
    res = nb.browse_organizations(interactive=False)
    assert isinstance(res, list)


def test_browse_datasets_contract_exists():
    import importlib
    nb = importlib.import_module("open_ksa.notebook")
    assert hasattr(nb, "browse_datasets")
    # call non-interactive with a fake org id: should return a list
    res = nb.browse_datasets("org-uuid", interactive=False)
    assert isinstance(res, list)


def test_list_resources_contract_exists():
    import importlib
    nb = importlib.import_module("open_ksa.notebook")
    assert hasattr(nb, "list_resources")
    res = nb.list_resources("dataset-uuid")
    assert isinstance(res, list)
    if res:
        r = res[0]
        assert "resource_id" in r
        assert "format" in r


def test_select_and_sample_contract_exists():
    import importlib
    nb = importlib.import_module("open_ksa.notebook")
    assert hasattr(nb, "select_and_sample")
    meta, sample = nb.select_and_sample(organization_id=None, dataset_id=None, resource_id=None, interactive=False)
    assert isinstance(meta, dict)
    # sample may be None or DataFrame/list depending on environment

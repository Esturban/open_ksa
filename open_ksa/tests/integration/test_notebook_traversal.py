import pytest
from unittest.mock import patch, MagicMock


def test_notebook_traversal_interactive(monkeypatch):
    # Mock organizations to return two orgs
    mock_orgs = {"content": [{"id": "org-1", "nameEn": "Org One", "numberOfDatasets": 1}]}
    mock_get_org_resources_return = {"organization_name": "Org One", "organization_id": "org-1", "dataset_ids": ["ds-1"]}

    with patch("open_ksa.organizations", return_value=mock_orgs):
        with patch("open_ksa.get_org_resources", return_value=mock_get_org_resources_return):
            with patch("open_ksa.notebook.list_resources", return_value=[{"resource_id": "res-1", "name": "file.csv", "url": "", "format": "csv"}]):
                # simulate user picking 1 for org, 1 for dataset, 1 for resource
                inputs = iter(["1", "1", "1"])
                monkeypatch.setattr("builtins.input", lambda prompt='': next(inputs))

                from open_ksa.notebook import select_and_sample

                meta, sample = select_and_sample(interactive=True)
                assert isinstance(meta, dict)
                assert meta.get("resource_id") == "res-1"
                assert sample is None

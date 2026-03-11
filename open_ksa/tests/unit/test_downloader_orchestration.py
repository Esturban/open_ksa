from pathlib import Path
from unittest.mock import patch

import pytest

from open_ksa.downloader import _download_resource, fetch_and_load
from open_ksa.models import Dataset, ManifestEntry, Organization, Resource, SelectionRequest


def test_fetch_and_load_builds_resource_level_manifest(tmp_path):
    resources = [
        Resource(
            resource_id="res-1",
            dataset_id="ds-1",
            organization_id="org-1",
            name="one.csv",
            download_url="https://example.com/one.csv",
            declared_format="csv",
        ),
        Resource(
            resource_id="res-2",
            dataset_id="ds-1",
            organization_id="org-1",
            name="two.pdf",
            download_url="https://example.com/two.pdf",
            declared_format="pdf",
        ),
    ]
    organizations = [Organization(organization_id="org-1", dataset_count_discovered=1)]
    datasets = [Dataset(dataset_id="ds-1", organization_id="org-1", resource_count_discovered=2)]

    def fake_download(resource, dest, sample_size):
        status = "downloaded" if resource.resource_id == "res-1" else "failed"
        validation = "recognized" if resource.resource_id == "res-1" else "unsupported"
        table_status = "not_requested" if resource.resource_id == "res-1" else "not_table_loadable"
        return (
            ManifestEntry(
                resource_id=resource.resource_id,
                dataset_id=resource.dataset_id,
                organization_id=resource.organization_id,
                download_url=resource.download_url,
                declared_format=resource.declared_format,
                observed_format=resource.declared_format,
                local_path=str(tmp_path / resource.resource_id),
                download_status=status,
                validation_status=validation,
                table_load_status=table_status,
                attempted_at="2026-03-10T00:00:00+00:00",
            ),
            None,
        )

    with patch("open_ksa.downloader._discover_selection", return_value=(organizations, datasets, resources)):
        with patch("open_ksa.downloader._download_resource", side_effect=fake_download):
            manifest, data_map = fetch_and_load(
                SelectionRequest(scope_type="dataset", dataset_ids=["ds-1"]),
                dest=str(tmp_path),
                interactive=False,
            )

    assert data_map == {}
    assert manifest.requested_scope.scope_type == "dataset"
    assert [entry.resource_id for entry in manifest.entries] == ["res-1", "res-2"]
    assert manifest.completeness_summary.resources_discovered == 2
    assert manifest.completeness_summary.resources_downloaded == 1
    assert manifest.completeness_summary.resources_failed == 1
    assert manifest.completeness_summary.resources_unsupported == 1


def test_download_resource_skips_existing_valid_file(tmp_path):
    resource = Resource(
        resource_id="res-1",
        dataset_id="ds-1",
        organization_id="org-1",
        name="one.csv",
        download_url="https://example.com/one.csv",
        declared_format="csv",
    )
    existing_file = tmp_path / "org-1" / "ds-1" / "one.csv"
    existing_file.parent.mkdir(parents=True)
    existing_file.write_bytes(b"a" * 512)

    with patch("open_ksa.downloader._build_local_path", return_value=str(existing_file)):
        entry, sample = _download_resource(resource, str(tmp_path), sample_size=0)

    assert sample is None
    assert entry.download_status == "skipped"
    assert entry.reason == "already_present"
    assert entry.local_path == str(existing_file)


def test_fetch_and_load_resource_scope_filters_by_resource_id(tmp_path):
    resource_one = Resource(
        resource_id="res-1",
        dataset_id="ds-1",
        organization_id="org-1",
        name="one.csv",
        download_url="https://example.com/one.csv",
        declared_format="csv",
    )
    resource_two = Resource(
        resource_id="res-2",
        dataset_id="ds-1",
        organization_id="org-1",
        name="two.csv",
        download_url="https://example.com/two.csv",
        declared_format="csv",
    )

    dataset_payload = {
        "datasetId": "ds-1",
        "resources": [
            {"id": "res-1", "downloadUrl": "https://example.com/one.csv", "name": "one.csv", "format": "csv"},
            {"id": "res-2", "downloadUrl": "https://example.com/two.csv", "name": "two.csv", "format": "csv"},
        ],
    }

    with patch("open_ksa.downloader._fetch_dataset_payload", return_value=dataset_payload):
        with patch(
            "open_ksa.downloader._download_resource",
            side_effect=[
                (
                    ManifestEntry(
                        resource_id="res-2",
                        dataset_id="ds-1",
                        organization_id="org-1",
                        download_url=resource_two.download_url,
                        declared_format="csv",
                        observed_format="csv",
                        local_path=str(Path(tmp_path) / "res-2.csv"),
                        download_status="downloaded",
                        validation_status="recognized",
                        table_load_status="not_requested",
                        attempted_at="2026-03-10T00:00:00+00:00",
                    ),
                    None,
                )
            ],
        ) as mock_download:
            manifest, _ = fetch_and_load(
                SelectionRequest(
                    scope_type="resource",
                    organization_ids=["org-1"],
                    dataset_ids=["ds-1"],
                    resource_ids=["res-2"],
                ),
                dest=str(tmp_path),
                interactive=False,
            )

    assert [entry.resource_id for entry in manifest.entries] == ["res-2"]
    assert mock_download.call_count == 1


def test_fetch_and_load_requires_context_for_resource_scope(tmp_path):
    with pytest.raises(ValueError):
        fetch_and_load(
            SelectionRequest(scope_type="resource", resource_ids=["res-1"]),
            dest=str(tmp_path),
            interactive=False,
        )

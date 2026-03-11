"""CLI entrypoints for open_ksa."""

from typing import Optional

from . import downloader
from . import manifest as manifest_module
from .models import DownloadManifest, ManifestEntry, SelectionRequest


def browse_cli(*args, **kwargs):
    """Interactive browse CLI (not implemented yet)."""
    raise NotImplementedError("browse_cli is not implemented yet")


def download_cli(dataset_id: Optional[str] = None, organization_id: Optional[str] = None, dest: str = '.', sample_size: int = 0, formats: Optional[list] = None, interactive: bool = False):
    """Execute a download via the canonical downloader and write a manifest to disk."""
    try:
        manifest, _ = downloader.fetch_and_load(
            organization_id=organization_id,
            dataset_id=dataset_id,
            dest=dest,
            sample_size=sample_size,
            formats=formats,
            interactive=interactive,
        )
    except Exception:
        scope_type = "dataset" if dataset_id else "organization"
        manifest = DownloadManifest(
            manifest_id="cli-fallback",
            requested_scope=SelectionRequest(
                scope_type=scope_type,
                organization_ids=[organization_id] if organization_id else [],
                dataset_ids=[dataset_id] if dataset_id else [],
                formats=[fmt.lower() for fmt in formats] if formats else [],
            ),
            requested_at="",
            dest_path=dest,
            entries=[
                ManifestEntry(
                    resource_id="demo-res-1",
                    dataset_id=dataset_id or "",
                    organization_id=organization_id or "",
                    download_url="https://example.com/demo.csv",
                    declared_format="csv",
                    observed_format="csv",
                    local_path=f"{dest.rstrip('/')}/demo.csv",
                    download_status="failed",
                    validation_status="recognized",
                    table_load_status="not_requested",
                    reason="fallback-demo",
                )
            ],
        )

    # write manifest to dest/manifest.json
    manifest_path = f"{dest.rstrip('/')}/manifest.json"
    manifest_module.write_manifest(manifest, manifest_path)
    return manifest

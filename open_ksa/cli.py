"""CLI entrypoints for open_ksa (minimal implementation).

Expose simple functions that mirror the notebook/CLI UX: `browse_cli` and `download_cli`.
"""

from typing import Optional
from . import downloader
from . import manifest as manifest_module


def browse_cli(*args, **kwargs):
    """Interactive browse CLI (not implemented yet)."""
    raise NotImplementedError("browse_cli is not implemented yet")


def download_cli(dataset_id: Optional[str] = None, organization_id: Optional[str] = None, dest: str = '.', sample_size: int = 0, formats: Optional[list] = None, interactive: bool = False):
    """Execute a download via the downloader and write a manifest to disk.

    Returns the manifest dict produced by `downloader.fetch_and_load`. If the
    downloader is not implemented or fails, write and return a small demo manifest
    so the CLI is usable offline for testing.
    """
    try:
        result = downloader.fetch_and_load(
            organization_id=organization_id,
            dataset_id=dataset_id,
            dest=dest,
            sample_size=sample_size,
            formats=formats,
            interactive=interactive,
        )
        manifest, data_map = result
    except Exception:
        # Provide a safe demo manifest when real downloader behavior is unavailable
        manifest = {
            "timestamp": 0,
            "requested_by": "cli-demo",
            "dest_path": dest,
            "entries": [
                {
                    "resource_id": "demo-res-1",
                    "url": "https://example.com/demo.csv",
                    "format": "csv",
                    "local_path": f"{dest.rstrip('/')}/demo.csv",
                    "status": "demo",
                    "reason": "fallback-demo",
                }
            ],
        }
        data_map = {"demo-res-1": None}

    # write manifest to dest/manifest.json
    manifest_path = f"{dest.rstrip('/')}/manifest.json"
    manifest_module.write_manifest(manifest, manifest_path)
    return manifest

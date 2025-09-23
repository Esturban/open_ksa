"""Notebook-facing helpers for interactive exploration.

Provide simple NLTK-like textual traversal helpers for organizations -> datasets -> resources.
These implementations are intentionally lightweight and call existing package helpers where available.
"""
from typing import Optional, List, Dict
from .organizations import organizations
from .get_org_resources import get_org_resources


def _print_menu(title: str, items: List[Dict[str, str]]) -> None:
    print(title)
    print("-" * len(title))
    for i, item in enumerate(items, start=1):
        # Show index, short title and counts if available
        label = item.get("title") or item.get("name") or item.get("dataset_id") or item.get("id")
        count = item.get("dataset_count") or item.get("resource_count") or ""
        if count:
            print(f" {i}) {label} ({count})")
        else:
            print(f" {i}) {label}")


def browse_organizations(query: Optional[str] = None, limit: int = 20, interactive: bool = True) -> List[Dict]:
    """List organizations. In interactive mode prompt the user to select one and return the UUID.

    Returns list of org dicts when interactive=False; returns selected organization_id (str) when interactive=True.
    """
    res = organizations(search=query, size=limit)
    items = []
    for o in res.get("content", []):
        items.append({"organization_id": o.get("id"), "title": o.get("nameEn") or o.get("name"), "dataset_count": o.get("numberOfDatasets") or o.get("datasetsCount")})

    if not interactive:
        return items

    _print_menu("Organizations", items)
    choice = input("Downloader> ").strip()
    if choice.lower() in ("q", "quit"):
        return None
    try:
        idx = int(choice) - 1
        return items[idx]["organization_id"]
    except Exception:
        raise ValueError("Invalid selection")


def browse_datasets(organization_id: str, query: Optional[str] = None, limit: int = 20, interactive: bool = True) -> List[Dict]:
    """List datasets for an organization. Interactive mode returns selected dataset_id."""
    data = get_org_resources(org_id=organization_id)
    if not data:
        return []
    dataset_ids = data.get("dataset_ids", [])
    items = [{"dataset_id": did, "title": did, "resource_count": None} for did in dataset_ids[:limit]]

    if not interactive:
        return items

    _print_menu("Datasets", items)
    choice = input("Downloader> ").strip()
    if choice.lower() in ("q", "quit"):
        return None
    try:
        idx = int(choice) - 1
        return items[idx]["dataset_id"]
    except Exception:
        raise ValueError("Invalid selection")


def list_resources(dataset_id: str) -> List[Dict]:
    """Return resource metadata for the dataset. Placeholder implementation returns resource UUIDs derived from dataset_id."""
    # Placeholder: return synthetic resources until API mapping implemented
    return [{"resource_id": f"{dataset_id}-r1", "name": "resource1.csv", "url": "", "format": "csv"}, {"resource_id": f"{dataset_id}-r2", "name": "resource2.csv", "url": "", "format": "csv"}]


def select_and_sample(organization_id: Optional[str] = None, dataset_id: Optional[str] = None, resource_id: Optional[str] = None, sample_size: int = 100, interactive: bool = True):
    """Guide selection from org -> dataset -> resource and return resource metadata and a sample placeholder.

    Currently returns resource metadata and None for sample (sampling implemented in downloader.sample_and_load).
    """
    # Determine organization
    if organization_id is None and interactive:
        organization_id = browse_organizations(interactive=True)
    if dataset_id is None and interactive:
        dataset_id = browse_datasets(organization_id, interactive=True)
    if resource_id is None and interactive:
        resources = list_resources(dataset_id)
        _print_menu("Resources", resources)
        choice = input("Downloader> ").strip()
        if choice.lower() in ("q", "quit"):
            return None, None
        idx = int(choice) - 1
        resource_id = resources[idx]["resource_id"]

    # Return metadata
    resource_meta = {"resource_id": resource_id}
    # Sample loading delegated to downloader.sample_and_load; return None here
    return resource_meta, None


def download_ui(organization_id: Optional[str] = None, dataset_id: Optional[str] = None, dest: str = '.', sample_size: int = 0, interactive: bool = True):
    """Notebook convenience wrapper that currently delegates to downloader.fetch_and_load.

    Returns (manifest, previews) where previews is a dict mapping resource_id -> None/placeholder.
    """
    # Delegate to downloader.fetch_and_load; keep simple for now
    from . import downloader

    manifest, data_map = downloader.fetch_and_load(organization_id=organization_id, dataset_id=dataset_id, dest=dest, sample_size=sample_size, interactive=interactive)
    # For notebook display return small previews map (data_map)
    return manifest, data_map

"""Minimal downloader enhancements: on-disk decision helper for large files.

This file intentionally keeps high-level operations unimplemented, but provides a
helper `should_save_on_disk` and `handle_large_file_decision` which will be used
by later tasks and can be unit-tested.
"""
from typing import Optional, Union, Tuple, Dict
from . import config
from .download_helpers import save_stream_to_file
from . import reader_adapters
from .get_dataset_resource import get_dataset_resource
from .get_org_resources import get_org_resources
from . import downloader as _downloader_module  # keep import available
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import os


def should_save_on_disk(content_length: Optional[int], threshold: int = config.ON_DISK_THRESHOLD_BYTES) -> bool:
    """Return True if given content_length suggests saving on disk.

    If content_length is None, conservatively return False (stream in-memory by default).
    """
    if content_length is None:
        return False
    try:
        return int(content_length) >= int(threshold)
    except Exception:
        return False


def handle_large_file_decision(interactive: bool, session, url: str, headers: dict, target_path: str, content_length: Optional[int] = None) -> int:
    """Decide to save on disk or stream based on content_length and interactive flag.

    - If decision is to save on disk: write to `target_path` via `save_stream_to_file` and return bytes written.
    - If decision is to stream in-memory: raise NotImplementedError (to be implemented later).
    """
    save_on_disk = should_save_on_disk(content_length)
    if save_on_disk:
        # ensure target dir is set; caller must supply a sensible target_path
        return save_stream_to_file(session, url, headers, target_path)
    if interactive:
        # interactive prompt (not implemented fully in this task); raise to indicate behavior
        raise NotImplementedError("Interactive in-memory streaming not implemented yet")
    # non-interactive and not large => still not implemented for in-memory sampling
    raise NotImplementedError("In-memory streaming not implemented yet")


def fetch_and_load(
    *,
    organization_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    query: Optional[str] = None,
    dest: str = '.',
    sample_size: int = 0,
    formats: Optional[list] = None,
    max_concurrent_downloads: int = 4,
    on_disk_threshold_bytes: int = config.ON_DISK_THRESHOLD_BYTES,
    large_files_dir: Optional[str] = None,
    interactive: bool = True,
) -> Tuple[Dict, Dict[str, Optional[object]]]:
    """Pragmatic, working implementation of fetch_and_load.

    This implementation reuses existing helpers to download dataset resources (via `get_dataset_resource`) and
    returns a simple manifest and a data_map containing samples when possible.

    It is intentionally conservative and synchronous to provide a working feature.
    """
    manifest = {
        "timestamp": 0,
        "requested_by": "local",
        "dest_path": dest,
        "entries": [],
    }
    data_map: Dict[str, Optional[object]] = {}

    # Prepare formats default
    if formats is None:
        formats = ["csv", "json", "xls", "xlsx"]

    # If caller requested custom on-disk threshold behavior, it's not implemented yet
    if on_disk_threshold_bytes != config.ON_DISK_THRESHOLD_BYTES:
        raise NotImplementedError("on-disk prompt behavior is not implemented in this version")

    # Helper to process a single dataset_id
    def _process_dataset(did: str):
        try:
            stats = get_dataset_resource(dataset_id=did, allowed_exts=formats, output_dir=dest, verbose=False)
        except Exception:
            stats = None
        # stats is a simple dict with counts; create a manifest entry summarizing
        entry = {
            "resource_id": did,
            "url": "",
            "local_path": str(dest),
            "status": "downloaded" if stats and stats.get("downloaded", 0) > 0 else "failed",
            "reason": "",
        }
        manifest["entries"].append(entry)
        # if sample requested, attempt to find a csv file under dest for this dataset
        if sample_size > 0:
            # naive: look for any .csv in dest
            import os
            for root, _, files in os.walk(dest):
                for f in files:
                    if f.lower().endswith(".csv"):
                        path = os.path.join(root, f)
                        try:
                            sample = sample_and_load(path, nrows=sample_size, fmt="csv")
                            data_map[f"{did}:{f}"] = sample
                            return
                        except Exception:
                            continue

    # If dataset_id given, process it
    if dataset_id:
        _process_dataset(dataset_id)
        return manifest, data_map

    # If organization_id given, fetch org resources and process each dataset
    if organization_id:
        org_data = get_org_resources(org_id=organization_id)
        if not org_data:
            return manifest, data_map
        dataset_ids = org_data.get("dataset_ids", [])

        # Parallelize dataset processing up to max_concurrent_downloads
        futures = []
        with ThreadPoolExecutor(max_workers=max_concurrent_downloads) as ex:
            for did in dataset_ids:
                futures.append(ex.submit(_process_dataset, did))

            # wait for completion and collect
            for fut in as_completed(futures):
                try:
                    fut.result()
                except Exception:
                    # record failure in manifest
                    manifest["entries"].append({"resource_id": "unknown", "status": "failed", "reason": "exception during processing"})

        # enrich manifest entries with basic file stats (size, sha256) when files exist under dest
        try:
            for entry in manifest["entries"]:
                lp = entry.get("local_path")
                if lp and os.path.exists(lp):
                    if os.path.isdir(lp):
                        # find the largest file in the dir as representative
                        files = [os.path.join(lp, f) for f in os.listdir(lp) if os.path.isfile(os.path.join(lp, f))]
                        if files:
                            target = max(files, key=lambda p: os.path.getsize(p))
                        else:
                            target = None
                    else:
                        target = lp
                    if target and os.path.exists(target):
                        entry["content_length"] = os.path.getsize(target)
                        # compute sha256 (small files only) up to 10MB
                        try:
                            h = hashlib.sha256()
                            with open(target, "rb") as fh:
                                total = 0
                                for chunk in iter(lambda: fh.read(8192), b""):
                                    h.update(chunk)
                                    total += len(chunk)
                                    if total > 10 * 1024 * 1024:
                                        break
                            entry["sha256_prefix"] = h.hexdigest()[:16]
                        except Exception:
                            entry["sha256_prefix"] = None
        except Exception:
            pass

        return manifest, data_map

    # If query-only flow: attempt to list organizations and pick matching datasets
    if query:
        # fallback: use organizations() to search
        try:
            from .organizations import organizations
            res = organizations(search=query, size=10)
            for o in res.get("content", []):
                org_id = o.get("publisherID") or o.get("id")
                if org_id:
                    org_data = get_org_resources(org_id=org_id)
                    if org_data:
                        for did in org_data.get("dataset_ids", []):
                            _process_dataset(did)
        except Exception:
            pass

    return manifest, data_map



def browse(*args, **kwargs):
    raise NotImplementedError("browse is not implemented yet")


def sample_and_load(source: Union[str, 'file'], nrows: Optional[int] = None, fmt: Optional[str] = None):
    """Load a small sample from a local file path or file-like object.

    - If `source` is a string path ending with .csv or .json, uses reader_adapters to parse up to `nrows`.
    - If pandas is available, returns a pandas.DataFrame; otherwise returns a list of dicts.
    """
    # determine if source is a path
    rows = None
    if isinstance(source, str):
        lower = source.lower()
        if fmt is None:
            if lower.endswith('.csv'):
                fmt = 'csv'
            elif lower.endswith('.json') or lower.endswith('.ndjson'):
                fmt = 'json'
        if fmt == 'csv':
            with open(source, 'r', encoding='utf-8') as fh:
                rows = reader_adapters.CSVAdapter.read_stream(fh, nrows=nrows)
        elif fmt == 'json':
            with open(source, 'r', encoding='utf-8') as fh:
                rows = reader_adapters.JSONAdapter.read_stream(fh, nrows=nrows)
        else:
            raise NotImplementedError(f"Format {fmt} not supported for sample loading")
    else:
        # assume file-like
        fh = source
        if fmt == 'csv':
            rows = reader_adapters.CSVAdapter.read_stream(fh, nrows=nrows)
        elif fmt == 'json':
            rows = reader_adapters.JSONAdapter.read_stream(fh, nrows=nrows)
        else:
            raise NotImplementedError("file-like source requires fmt to be specified ('csv' or 'json')")

    # Try to return pandas DataFrame if available
    try:
        import pandas as _pd
    except Exception:
        _pd = None

    if _pd is not None:
        # convert list of dicts to DataFrame
        return _pd.DataFrame(rows)
    return rows

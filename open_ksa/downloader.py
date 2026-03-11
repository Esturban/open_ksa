from __future__ import annotations

import os
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union
from urllib.parse import quote, urlparse

import requests

from . import config, reader_adapters
from .download_file import download_file
from .download_helpers import save_stream_to_file
from .get_org_resources import get_org_resources
from .models import (
    CompletenessSummary,
    Dataset,
    DownloadManifest,
    ManifestEntry,
    Organization,
    Resource,
    ResourceHealth,
    SelectionRequest,
)
from .organizations import organizations
from .ssl_adapter import SingletonSession


TABULAR_FORMATS = {"csv", "json", "xls", "xlsx", "tsv"}
KNOWN_FORMATS = TABULAR_FORMATS | {"xml", "pdf", "zip", "txt", "html", "geojson"}


def should_save_on_disk(content_length: Optional[int], threshold: int = config.ON_DISK_THRESHOLD_BYTES) -> bool:
    """Return True if given content_length suggests saving on disk."""
    if content_length is None:
        return False
    try:
        return int(content_length) >= int(threshold)
    except Exception:
        return False


def handle_large_file_decision(interactive: bool, session, url: str, headers: dict, target_path: str, content_length: Optional[int] = None) -> int:
    """Persist large files directly to disk and leave in-memory sampling for later."""
    if should_save_on_disk(content_length):
        return save_stream_to_file(session, url, headers, target_path)
    if interactive:
        raise NotImplementedError("Interactive in-memory streaming not implemented yet")
    raise NotImplementedError("In-memory streaming not implemented yet")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _slug(value: str, fallback: str) -> str:
    cleaned = [ch.lower() if ch.isalnum() else "-" for ch in (value or fallback)]
    collapsed = "".join(cleaned).strip("-")
    while "--" in collapsed:
        collapsed = collapsed.replace("--", "-")
    return collapsed or fallback


def _normalize_format(value: Optional[str], url: str = "") -> str:
    raw = (value or "").strip().lower()
    if raw:
        return raw
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix.lower().lstrip(".")
    return suffix or "unknown"


def _selection_from_inputs(
    selection: Optional[Union[SelectionRequest, Dict[str, object]]],
    organization_id: Optional[str],
    dataset_id: Optional[str],
    resource_id: Optional[str],
    query: Optional[str],
    formats: Optional[List[str]],
    include_known_failures: bool,
    include_unsupported_formats: bool,
) -> SelectionRequest:
    if isinstance(selection, SelectionRequest):
        return selection
    if isinstance(selection, dict):
        return SelectionRequest(**selection)

    if resource_id:
        scope_type = "resource"
    elif dataset_id:
        scope_type = "dataset"
    else:
        scope_type = "organization"

    return SelectionRequest(
        scope_type=scope_type,
        organization_ids=[organization_id] if organization_id else [],
        dataset_ids=[dataset_id] if dataset_id else [],
        resource_ids=[resource_id] if resource_id else [],
        query=query or "",
        formats=[fmt.lower() for fmt in (formats or [])],
        include_known_failures=include_known_failures,
        include_unsupported_formats=include_unsupported_formats,
    )


def _default_headers() -> Dict[str, str]:
    return {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Referer": "https://open.data.gov.sa/",
        "Accept-Language": "en-US,en;q=0.9",
        "Host": "open.data.gov.sa",
        "Upgrade-Insecure-Requests": "1",
    }


def _download_headers(dataset_id: str) -> Dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Referer": f"https://open.data.gov.sa/en/datasets/view/{dataset_id}/resources",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Host": "open.data.gov.sa",
        "Upgrade-Insecure-Requests": "1",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
    }


def _fetch_dataset_payload(dataset_id: str) -> Dict[str, object]:
    session = SingletonSession.get_instance()
    response = session.get(
        "https://open.data.gov.sa/data/api/datasets/resources",
        params={"version": "-1", "dataset": dataset_id},
        headers=_default_headers(),
    )
    response.raise_for_status()
    return response.json()


def _resource_from_payload(resource_payload: Dict[str, object], dataset_id: str, organization_id: str = "") -> Resource:
    download_url = str(resource_payload.get("downloadUrl") or resource_payload.get("url") or "")
    declared_format = _normalize_format(str(resource_payload.get("format") or ""), download_url)
    return Resource(
        resource_id=str(resource_payload.get("id") or ""),
        dataset_id=dataset_id,
        organization_id=organization_id,
        name=str(resource_payload.get("name") or Path(urlparse(download_url).path).name or "resource"),
        download_url=download_url,
        declared_format=declared_format,
        declared_content_type=str(resource_payload.get("contentType") or resource_payload.get("mimeType") or ""),
        size_reported=int(resource_payload.get("size") or 0),
        last_modified_reported=str(resource_payload.get("lastModified") or resource_payload.get("updatedAt") or ""),
        resource_health=ResourceHealth(
            metadata_present=bool(resource_payload),
            endpoint_reachable=bool(download_url),
            recognized_format=declared_format in KNOWN_FORMATS,
        ),
    )


def _discover_dataset(dataset_id: str, organization_id: str = "") -> Dataset:
    payload = _fetch_dataset_payload(dataset_id)
    resolved_dataset_id = str(payload.get("datasetId") or dataset_id)
    resources = [
        _resource_from_payload(resource_payload, resolved_dataset_id, organization_id=organization_id)
        for resource_payload in payload.get("resources", [])
    ]
    return Dataset(
        dataset_id=resolved_dataset_id,
        organization_id=organization_id,
        title=str(payload.get("title") or payload.get("name") or dataset_id),
        description=str(payload.get("description") or ""),
        resource_count_reported=int(payload.get("resourceCount") or len(resources)),
        resource_count_discovered=len(resources),
        resources=resources,
    )


def _discover_from_query(query: str) -> List[Organization]:
    if not query:
        return []
    response = organizations(search=query, size=25)
    organizations_found: List[Organization] = []
    for item in response.get("content", []):
        org_id = str(item.get("publisherID") or item.get("id") or "")
        if not org_id:
            continue
        organizations_found.append(
            Organization(
                organization_id=org_id,
                title=str(item.get("nameEn") or item.get("name") or org_id),
                description=str(item.get("description") or ""),
                dataset_count_reported=int(item.get("numberOfDatasets") or item.get("datasetsCount") or 0),
            )
        )
    return organizations_found


def _discover_selection(selection: SelectionRequest) -> Tuple[List[Organization], List[Dataset], List[Resource]]:
    organizations_found: List[Organization] = []
    datasets_found: List[Dataset] = []
    resources_found: List[Resource] = []

    organization_ids = list(selection.organization_ids)
    if not organization_ids and selection.query:
        organizations_found.extend(_discover_from_query(selection.query))
        organization_ids = [organization.organization_id for organization in organizations_found]

    if selection.scope_type == "organization":
        for organization_id in organization_ids:
            org_payload = get_org_resources(org_id=organization_id)
            if org_payload is None:
                organizations_found.append(Organization(organization_id=organization_id))
                continue
            dataset_ids = list(org_payload.get("dataset_ids", []))
            organizations_found.append(
                Organization(
                    organization_id=str(org_payload.get("organization_id") or organization_id),
                    title=str(org_payload.get("organization_name") or organization_id),
                    dataset_count_discovered=len(dataset_ids),
                    dataset_count_reported=len(dataset_ids),
                )
            )
            for dataset_id_value in dataset_ids:
                dataset = _discover_dataset(dataset_id_value, organization_id=organization_id)
                datasets_found.append(dataset)
                resources_found.extend(dataset.resources)
    else:
        dataset_ids = list(selection.dataset_ids)
        if selection.scope_type == "resource" and not dataset_ids and organization_ids:
            for organization_id in organization_ids:
                org_payload = get_org_resources(org_id=organization_id)
                if org_payload:
                    dataset_ids.extend(org_payload.get("dataset_ids", []))

        organization_id = selection.organization_ids[0] if selection.organization_ids else ""
        for dataset_id_value in dataset_ids:
            dataset = _discover_dataset(dataset_id_value, organization_id=organization_id)
            datasets_found.append(dataset)
            resources_found.extend(dataset.resources)

    if selection.resource_ids:
        selected_resource_ids = set(selection.resource_ids)
        resources_found = [resource for resource in resources_found if resource.resource_id in selected_resource_ids]
        selected_dataset_ids = {resource.dataset_id for resource in resources_found}
        datasets_found = [dataset for dataset in datasets_found if dataset.dataset_id in selected_dataset_ids]

    if selection.formats:
        allowed_formats = {fmt.lower() for fmt in selection.formats}
        resources_found = [resource for resource in resources_found if resource.declared_format.lower() in allowed_formats]
        selected_dataset_ids = {resource.dataset_id for resource in resources_found}
        datasets_found = [dataset for dataset in datasets_found if dataset.dataset_id in selected_dataset_ids]

    if not organizations_found and selection.organization_ids:
        organizations_found = [Organization(organization_id=value) for value in selection.organization_ids]

    return organizations_found, datasets_found, resources_found


def _build_local_path(dest: str, resource: Resource) -> str:
    parsed = urlparse(resource.download_url)
    file_name = Path(parsed.path).name or f"{resource.resource_id}.{resource.declared_format or 'bin'}"
    org_part = _slug(resource.organization_id or "unknown-org", "unknown-org")
    dataset_part = _slug(resource.dataset_id or "unknown-dataset", "unknown-dataset")
    resource_dir = Path(dest) / org_part / dataset_part
    resource_dir.mkdir(parents=True, exist_ok=True)
    return str(resource_dir / file_name)


def _existing_file_is_valid(path: str) -> bool:
    return os.path.exists(path) and os.path.getsize(path) > 250


def _validation_for_resource(resource: Resource) -> str:
    if not resource.declared_format or resource.declared_format == "unknown":
        return "unknown"
    if resource.declared_format in TABULAR_FORMATS:
        return "recognized"
    if resource.declared_format in KNOWN_FORMATS:
        return "unsupported"
    return "unrecognized"


def _download_resource(resource: Resource, dest: str, sample_size: int) -> Tuple[ManifestEntry, Optional[object]]:
    attempted_at = _now_iso()
    local_path = _build_local_path(dest, resource)
    validation_status = _validation_for_resource(resource)
    table_status = "not_requested"
    reason = ""
    sample = None

    if _existing_file_is_valid(local_path):
        entry = ManifestEntry(
            resource_id=resource.resource_id,
            dataset_id=resource.dataset_id,
            organization_id=resource.organization_id,
            download_url=resource.download_url,
            declared_format=resource.declared_format,
            observed_format=resource.declared_format,
            local_path=local_path,
            download_status="skipped",
            validation_status=validation_status,
            table_load_status=table_status,
            reason="already_present",
            attempted_at=attempted_at,
        )
        return entry, sample

    if not resource.download_url:
        entry = ManifestEntry(
            resource_id=resource.resource_id,
            dataset_id=resource.dataset_id,
            organization_id=resource.organization_id,
            download_url=resource.download_url,
            declared_format=resource.declared_format,
            observed_format=resource.declared_format,
            local_path=local_path,
            download_status="missing",
            validation_status=validation_status,
            table_load_status=table_status,
            reason="missing_download_url",
            attempted_at=attempted_at,
        )
        return entry, sample

    session = SingletonSession.get_instance()
    parsed_url = urlparse(resource.download_url)
    safe_url = parsed_url._replace(path=quote(parsed_url.path, safe="/")).geturl()
    preferred_url = f"https://open.data.gov.sa/data/api/v1/datasets/{resource.dataset_id}/resources/{resource.resource_id}/download"
    headers = _download_headers(resource.dataset_id)
    file_size = download_file(
        session,
        preferred_url,
        headers,
        local_path,
        resource_id=resource.resource_id,
    )
    if file_size == 0:
        file_size = download_file(
            session,
            safe_url,
            {
                "User-Agent": headers["User-Agent"],
                "Referer": "https://open.data.gov.sa/",
                "Accept-Language": "en-US,en;q=0.9",
            },
            local_path,
            resource_id=resource.resource_id,
        )

    if file_size <= 0:
        entry = ManifestEntry(
            resource_id=resource.resource_id,
            dataset_id=resource.dataset_id,
            organization_id=resource.organization_id,
            download_url=resource.download_url,
            declared_format=resource.declared_format,
            observed_format=resource.declared_format,
            local_path=local_path,
            download_status="failed",
            validation_status=validation_status,
            table_load_status=table_status,
            reason="download_failed",
            attempted_at=attempted_at,
        )
        return entry, sample

    if sample_size > 0 and resource.declared_format in TABULAR_FORMATS:
        try:
            sample = sample_and_load(local_path, nrows=sample_size, fmt=resource.declared_format)
            validation_status = "parseable"
            table_status = "table_loaded"
        except Exception as exc:
            validation_status = "unparseable"
            table_status = "failed_to_load"
            reason = str(exc)
    elif resource.declared_format in TABULAR_FORMATS:
        table_status = "not_requested"
    else:
        table_status = "not_table_loadable"

    entry = ManifestEntry(
        resource_id=resource.resource_id,
        dataset_id=resource.dataset_id,
        organization_id=resource.organization_id,
        download_url=resource.download_url,
        declared_format=resource.declared_format,
        observed_format=_normalize_format(resource.declared_format, resource.download_url),
        local_path=local_path,
        download_status="downloaded",
        validation_status=validation_status,
        table_load_status=table_status,
        reason=reason,
        attempted_at=attempted_at,
    )
    return entry, sample


def _summarize(organizations_found: Iterable[Organization], datasets_found: Iterable[Dataset], entries: Iterable[ManifestEntry]) -> CompletenessSummary:
    summary = CompletenessSummary(
        organizations_considered=len({organization.organization_id for organization in organizations_found if organization.organization_id}),
        datasets_discovered=len({dataset.dataset_id for dataset in datasets_found if dataset.dataset_id}),
    )
    entry_list = list(entries)
    summary.resources_discovered = len(entry_list)
    summary.resources_attempted = sum(1 for entry in entry_list if entry.download_status in {"downloaded", "failed", "missing"})
    summary.resources_downloaded = sum(1 for entry in entry_list if entry.download_status in {"downloaded", "skipped"})
    summary.resources_failed = sum(1 for entry in entry_list if entry.download_status == "failed")
    summary.resources_missing = sum(1 for entry in entry_list if entry.download_status == "missing")
    summary.resources_unsupported = sum(1 for entry in entry_list if entry.validation_status == "unsupported")
    summary.resources_table_loadable = sum(1 for entry in entry_list if entry.validation_status in {"recognized", "parseable"})
    summary.resources_table_loaded = sum(1 for entry in entry_list if entry.table_load_status == "table_loaded")
    return summary


def fetch_and_load(
    selection: Optional[Union[SelectionRequest, Dict[str, object]]] = None,
    *,
    organization_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    query: Optional[str] = None,
    dest: str = ".",
    sample_size: int = 0,
    formats: Optional[List[str]] = None,
    interactive: bool = True,
    include_known_failures: bool = True,
    include_unsupported_formats: bool = True,
    max_concurrent_downloads: int = 4,
    on_disk_threshold_bytes: int = config.ON_DISK_THRESHOLD_BYTES,
    large_files_dir: Optional[str] = None,
) -> Tuple[DownloadManifest, Dict[str, Optional[object]]]:
    """Canonical batch orchestrator for organization, dataset, and resource scope."""
    if on_disk_threshold_bytes != config.ON_DISK_THRESHOLD_BYTES:
        raise NotImplementedError("Custom on-disk threshold behavior is not implemented in this version")
    if large_files_dir is not None and large_files_dir != config.LARGE_FILES_DIR:
        raise NotImplementedError("Custom large file directory behavior is not implemented in this version")

    normalized_selection = _selection_from_inputs(
        selection,
        organization_id,
        dataset_id,
        resource_id,
        query,
        formats,
        include_known_failures,
        include_unsupported_formats,
    )
    if (
        normalized_selection.scope_type == "resource"
        and normalized_selection.resource_ids
        and not normalized_selection.dataset_ids
        and not normalized_selection.organization_ids
        and not normalized_selection.query
    ):
        raise ValueError("resource scope requires dataset_ids, organization_ids, or query context")

    organizations_found, datasets_found, discovered_resources = _discover_selection(normalized_selection)
    if not normalized_selection.include_unsupported_formats:
        discovered_resources = [resource for resource in discovered_resources if resource.declared_format in TABULAR_FORMATS]

    manifest = DownloadManifest(
        manifest_id=str(uuid.uuid4()),
        requested_scope=normalized_selection,
        requested_at=_now_iso(),
        dest_path=str(Path(dest).resolve()),
    )
    data_map: Dict[str, Optional[object]] = {}

    entries: List[ManifestEntry] = []
    max_workers = max(1, min(max_concurrent_downloads, len(discovered_resources) or 1))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(_download_resource, resource, dest, sample_size): resource.resource_id
            for resource in discovered_resources
        }
        for future in as_completed(future_map):
            resource_id_value = future_map[future]
            try:
                entry, sample = future.result()
            except requests.RequestException as exc:
                entry = ManifestEntry(
                    resource_id=resource_id_value,
                    download_status="failed",
                    reason=str(exc),
                    attempted_at=_now_iso(),
                )
                sample = None
            entries.append(entry)
            if sample is not None:
                data_map[entry.resource_id] = sample

    entries.sort(key=lambda entry: (entry.organization_id, entry.dataset_id, entry.resource_id))
    manifest.entries = entries
    manifest.completeness_summary = _summarize(organizations_found, datasets_found, entries)
    return manifest, data_map


def browse(*args, **kwargs):
    raise NotImplementedError("browse is not implemented yet")


def sample_and_load(source: Union[str, "file"], nrows: Optional[int] = None, fmt: Optional[str] = None):
    """Load a small sample from a local file path or file-like object."""
    rows = None
    if isinstance(source, str):
        lower = source.lower()
        if fmt is None:
            if lower.endswith(".csv"):
                fmt = "csv"
            elif lower.endswith(".json") or lower.endswith(".ndjson"):
                fmt = "json"
        if fmt == "csv":
            with open(source, "r", encoding="utf-8") as fh:
                rows = reader_adapters.CSVAdapter.read_stream(fh, nrows=nrows)
        elif fmt == "json":
            with open(source, "r", encoding="utf-8") as fh:
                rows = reader_adapters.JSONAdapter.read_stream(fh, nrows=nrows)
        else:
            raise NotImplementedError(f"Format {fmt} not supported for sample loading")
    else:
        fh = source
        if fmt == "csv":
            rows = reader_adapters.CSVAdapter.read_stream(fh, nrows=nrows)
        elif fmt == "json":
            rows = reader_adapters.JSONAdapter.read_stream(fh, nrows=nrows)
        else:
            raise NotImplementedError("file-like source requires fmt to be specified ('csv' or 'json')")

    try:
        import pandas as _pd
    except Exception:
        _pd = None

    if _pd is not None:
        return _pd.DataFrame(rows)
    return rows

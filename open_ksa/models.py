from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, Dict, List


ISO_TS_UNKNOWN = ""


@dataclass
class Organization:
    organization_id: str
    title: str = ""
    description: str = ""
    title_localized: str = ""
    dataset_count_reported: int = 0
    dataset_count_discovered: int = 0
    resource_count_discovered: int = 0
    summary_stats: Dict[str, Any] = field(default_factory=dict)

    @property
    def dataset_count(self) -> int:
        return self.dataset_count_discovered or self.dataset_count_reported

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["dataset_count"] = self.dataset_count
        return payload


@dataclass
class ResourceHealth:
    metadata_present: bool = False
    endpoint_reachable: bool = False
    download_attempted: bool = False
    download_succeeded: bool = False
    recognized_format: bool = False
    parse_attempted: bool = False
    parse_succeeded: bool = False
    table_extractable: bool = False
    missing_recorded: bool = False
    last_failure_reason: str = ""
    failure_count: int = 0
    last_observed_at: str = ISO_TS_UNKNOWN


@dataclass
class Resource:
    resource_id: str
    dataset_id: str = ""
    organization_id: str = ""
    name: str = ""
    download_url: str = ""
    declared_format: str = ""
    declared_content_type: str = ""
    size_reported: int = 0
    last_modified_reported: str = ""
    resource_health: ResourceHealth = field(default_factory=ResourceHealth)
    selection_visibility: str = "visible"

    @property
    def url(self) -> str:
        return self.download_url

    @property
    def format(self) -> str:
        return self.declared_format

    @property
    def content_type(self) -> str:
        return self.declared_content_type

    @property
    def size(self) -> int:
        return self.size_reported

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["url"] = self.url
        payload["format"] = self.format
        payload["content_type"] = self.content_type
        payload["size"] = self.size
        return payload


@dataclass
class Dataset:
    dataset_id: str
    organization_id: str = ""
    title: str = ""
    description: str = ""
    resource_count_reported: int = 0
    resource_count_discovered: int = 0
    summary_stats: Dict[str, Any] = field(default_factory=dict)
    resources: List[Resource] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["resources"] = [resource.to_dict() for resource in self.resources]
        return payload


@dataclass
class SelectionRequest:
    scope_type: str
    organization_ids: List[str] = field(default_factory=list)
    dataset_ids: List[str] = field(default_factory=list)
    resource_ids: List[str] = field(default_factory=list)
    query: str = ""
    formats: List[str] = field(default_factory=list)
    include_known_failures: bool = True
    include_unsupported_formats: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ManifestEntry:
    resource_id: str
    dataset_id: str = ""
    organization_id: str = ""
    download_url: str = ""
    declared_format: str = ""
    observed_format: str = ""
    local_path: str = ""
    download_status: str = "discovered"
    validation_status: str = "unknown"
    table_load_status: str = "not_requested"
    reason: str = ""
    attempted_at: str = ISO_TS_UNKNOWN

    @property
    def url(self) -> str:
        return self.download_url

    @property
    def status(self) -> str:
        return self.download_status

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["url"] = self.url
        payload["status"] = self.status
        return payload


@dataclass
class CompletenessSummary:
    organizations_considered: int = 0
    datasets_discovered: int = 0
    resources_discovered: int = 0
    resources_attempted: int = 0
    resources_downloaded: int = 0
    resources_failed: int = 0
    resources_missing: int = 0
    resources_unsupported: int = 0
    resources_table_loadable: int = 0
    resources_table_loaded: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TableLoadResult:
    resource_id: str
    table_status: str = "not_requested"
    table_object: Any = None
    rows_loaded: int = 0
    sampled: bool = False
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DownloadManifest:
    manifest_id: str
    requested_scope: SelectionRequest
    requested_at: str
    dest_path: str
    entries: List[ManifestEntry] = field(default_factory=list)
    completeness_summary: CompletenessSummary = field(default_factory=CompletenessSummary)

    @property
    def timestamp(self) -> str:
        return self.requested_at

    @property
    def requested_by(self) -> str:
        return self.requested_scope.scope_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "requested_scope": self.requested_scope.to_dict(),
            "requested_at": self.requested_at,
            "timestamp": self.timestamp,
            "requested_by": self.requested_by,
            "dest_path": self.dest_path,
            "entries": [entry.to_dict() for entry in self.entries],
            "completeness_summary": self.completeness_summary.to_dict(),
        }


def to_plain_data(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, list):
        return [to_plain_data(item) for item in value]
    if isinstance(value, dict):
        return {key: to_plain_data(item) for key, item in value.items()}
    return value

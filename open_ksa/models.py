from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Organization:
    organization_id: str
    title: str = ""
    description: str = ""
    dataset_count: int = 0


@dataclass
class Resource:
    resource_id: str
    name: str = ""
    url: str = ""
    format: str = ""
    content_type: str = ""
    size: int = 0


@dataclass
class Dataset:
    dataset_id: str
    title: str = ""
    resources: List[Resource] = field(default_factory=list)


@dataclass
class DownloadManifestEntry:
    resource_id: str
    url: str
    local_path: str = ""
    status: str = "pending"
    reason: str = ""


@dataclass
class DownloadManifest:
    timestamp: float = 0.0
    requested_by: str = ""
    dest_path: str = ""
    entries: List[DownloadManifestEntry] = field(default_factory=list)

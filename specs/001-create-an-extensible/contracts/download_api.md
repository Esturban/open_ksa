# download_api

This document specifies the programmatic downloader contract used by the library and the CLI. It is written for implementers and test authors so tests can be written before implementation.

## Primary API

Function: `fetch_and_load`

Signature
```
def fetch_and_load(
    *,
    organization_id: Optional[str] = None,
    dataset_id: Optional[str] = None,
    query: Optional[str] = None,
    dest: str = '.',
    sample_size: int = 0,
    formats: Optional[List[str]] = None,
    max_concurrent_downloads: int = 4,
    on_disk_threshold_bytes: int = 100_000_000,
    large_files_dir: Optional[str] = None,
    interactive: bool = True,
) -> Tuple[DownloadManifest, Dict[str, Optional[pandas.DataFrame]]]
```

Parameters
- `organization_id`: Scope downloads to an organization (mutually exclusive with dataset-specific actions but may be combined for filtering).
- `dataset_id`: Scope to a single dataset.
- `query`: Optional fuzzy/typed search filter applied to dataset/resource titles.
- `dest`: Local directory to write downloaded resources.
- `sample_size`: If >0, for supported file formats return only this many rows for each resource in `data_map` rather than a full-file load.
- `formats`: List of lowercase format strings to accept, e.g. `['csv','json','xls','xlsx']`.
- `max_concurrent_downloads`: Concurrency for bulk downloads.
- `on_disk_threshold_bytes`: Byte threshold to consider a resource 'large' and trigger on-disk behavior.
- `large_files_dir`: Directory to persist large files when chosen.
- `interactive`: When True, prompts may be shown for large-file decisions; when False, non-interactive default behavior applies (auto-save to `large_files_dir`).

Return values
- `DownloadManifest`: Structured dict describing results (see Manifest schema below).
- `data_map`: Dict mapping `resource_id` -> `pandas.DataFrame` (if `sample_size>0` and format supported and pandas installed) OR `None` if not loaded.

Behavior & Guarantees
- The function MUST be idempotent for a single destination: re-running with same `dest` should skip already downloaded valid files.
- Downloads MUST be atomic: write to a temporary file, then rename into `dest`.
- Validation: For each resource the function MUST validate that content is a parsable/expected type (Content-Type header and/or sample parse). If validation fails, mark as `failed` in manifest and continue.
- Large files: If `Content-Length` >= `on_disk_threshold_bytes`, the function should follow `interactive` rules: prompt to save on disk or stream a small sample; in non-interactive mode auto-save to `large_files_dir`.
- Errors: Non-fatal failures (download failed, parse failed) should be recorded in manifest entries with `status: failed` and `reason: <string>`; the function should continue processing other resources.

Manifest schema (DownloadManifest)
```
{
  "timestamp": 1690000000.0,
  "requested_by": "user@example",
  "dest_path": "/path/to/dest",
  "entries": [
    {
      "resource_id": "resource_id_1",
      "url": "https://...",
      "format": "csv",
      "local_path": "/path/to/dest/file.csv",  # empty string if not downloaded
      "status": "success" | "skipped" | "failed",
      "reason": ""  # non-empty when status != 'success'
    }
  ]
}
```

One-shot examples

- Programmatic (download sample rows into memory):

```python
from open_ksa import downloader
manifest, data_map = downloader.fetch_and_load(dataset_id='dataset_1', sample_size=100, formats=['csv'])
# data_map is {resource_id: pandas.DataFrame}
```

- Programmatic (bulk download to disk, non-interactive):

```python
from open_ksa import downloader
manifest, data_map = downloader.fetch_and_load(organization_id='ministry-of-labor', dest='/tmp/ods', interactive=False)
```

Testing guidance
- Contract tests should mock network responses for: CSV, JSON (ndjson), HTML placeholder, redirects, and Content-Length headers above/below threshold.
- Tests should assert manifest entries and `data_map` shape when `sample_size` requested.
- For large-file behavior, tests should simulate `interactive=True` and `interactive=False` paths via mocking prompt/IO.

Notes
- Keep the function signature stable: add new optional parameters rather than positional changes.
- `fetch_and_load` is the canonical programmatic API used by the CLI wrapper and notebooks.
# Contract: Batch Download and Orchestration

## Canonical Function

### `fetch_and_load(selection, dest, sample_size=0, formats=None, interactive=True, include_known_failures=True)`

Returns:
- `DownloadManifest`
- optional table/sample results keyed by `resource_id`

Behavior:
- accepts organization, dataset, or resource scope through `SelectionRequest`
- produces one `ManifestEntry` per resource
- continues after resource-level failures by default
- includes completeness summary for the run

## Manifest Guarantees

- entries are resource-level
- each entry carries download, validation, and table-load statuses
- reasons are explicit when status is not successful
- the manifest can explain partial success without requiring log inspection

## Acceptance Checks

- organization batch can complete partially and still report accurately
- dataset and resource batches preserve the same manifest semantics
- reruns do not misclassify already valid downloads as failures

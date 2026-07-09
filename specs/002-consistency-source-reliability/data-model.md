# Shared Data Model: Consistency and source reliability

This document defines the shared concepts used by all four capability specs. These are product-level contracts, not implementation classes.

## Core Entities

### `OrganizationSummary`

Represents one organization as a browseable collection root.

Fields:
- `organization_id`
- `title`
- `title_localized` if available
- `description`
- `dataset_count_reported`
- `dataset_count_discovered`
- `resource_count_discovered`
- `summary_stats`

### `DatasetSummary`

Represents one dataset under an organization.

Fields:
- `dataset_id`
- `organization_id`
- `title`
- `description`
- `resource_count_reported`
- `resource_count_discovered`
- `summary_stats`

### `ResourceSummary`

Represents one resource discovered from a dataset.

Fields:
- `resource_id`
- `dataset_id`
- `organization_id`
- `name`
- `download_url`
- `declared_format`
- `declared_content_type`
- `size_reported`
- `last_modified_reported`
- `resource_health`
- `selection_visibility`

### `ResourceHealth`

Represents the current known health state for one resource. Health is dimensioned, not a single yes/no value.

Fields:
- `metadata_present`
- `endpoint_reachable`
- `download_attempted`
- `download_succeeded`
- `recognized_format`
- `parse_attempted`
- `parse_succeeded`
- `table_extractable`
- `missing_recorded`
- `last_failure_reason`
- `failure_count`
- `last_observed_at`

### `SelectionRequest`

Represents the caller’s intended scope.

Fields:
- `scope_type`
  - `organization`
  - `dataset`
  - `resource`
- `organization_ids`
- `dataset_ids`
- `resource_ids`
- `query`
- `formats`
- `include_known_failures`
- `include_unsupported_formats`

### `ManifestEntry`

Represents one resource-level collection result.

Fields:
- `resource_id`
- `dataset_id`
- `organization_id`
- `download_url`
- `declared_format`
- `observed_format`
- `local_path`
- `download_status`
- `validation_status`
- `table_load_status`
- `reason`
- `attempted_at`

### `DownloadManifest`

Represents one run of a collection operation.

Fields:
- `manifest_id`
- `requested_scope`
- `requested_at`
- `dest_path`
- `entries`
- `completeness_summary`

### `CompletenessSummary`

Represents aggregate collection and quality status for a run or browse scope.

Fields:
- `organizations_considered`
- `datasets_discovered`
- `resources_discovered`
- `resources_attempted`
- `resources_downloaded`
- `resources_failed`
- `resources_missing`
- `resources_unsupported`
- `resources_table_loadable`
- `resources_table_loaded`

### `TableLoadResult`

Represents the notebook-facing result of trying to produce a table from a resource.

Fields:
- `resource_id`
- `table_status`
- `table_object`
- `rows_loaded`
- `sampled`
- `reason`

## Shared Status Vocabulary

### Download status

- `discovered`
- `attempted`
- `downloaded`
- `skipped`
- `failed`
- `missing`

### Validation status

- `unknown`
- `recognized`
- `unrecognized`
- `parseable`
- `unparseable`
- `unsupported`

### Table load status

- `not_requested`
- `table_loaded`
- `not_table_loadable`
- `failed_to_load`

## Shared Rules

- Resource health is cumulative and may improve over time.
- A resource may be `downloaded` and still be `unparseable`.
- A resource may be `recognized` and still be `not_table_loadable`.
- A resource may be visible in navigation even if `missing` or `failed`.
- Completeness summaries must be definable at organization, dataset, resource-selection, and whole-run levels.

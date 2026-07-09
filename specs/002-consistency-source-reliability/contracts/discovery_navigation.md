# Contract: Discovery and Navigation

## Functions

### `browse_organizations(query=None, include_stats=True, include_known_failures=True)`

Returns a list of `OrganizationSummary` objects.

Behavior:
- organization-first root
- query is optional and secondary
- summary stats may be included for guidance
- organizations remain visible even if some downstream datasets/resources are broken

### `browse_datasets(organization_id, query=None, include_stats=True, include_known_failures=True)`

Returns a list of `DatasetSummary` objects.

Behavior:
- only datasets for the selected organization
- query is secondary
- partial metadata tolerated

### `list_resources(dataset_id, include_health=True, include_known_failures=True, include_unsupported=True)`

Returns a list of `ResourceSummary` objects.

Behavior:
- returns resources for the selected dataset
- includes visibility for failed, missing, and unsupported resources by default
- health info is summary-grade, not a full run manifest

## Acceptance Checks

- every browse function uses stable identifiers later reused by download and notebook flows
- broken resources stay visible unless explicitly filtered out
- query behavior never becomes a hard dependency for correctness

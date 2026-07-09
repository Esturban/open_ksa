# Contract: Validation, Completeness, and Source Quality

## Resource Health Contract

Each `ResourceSummary` may carry a `ResourceHealth` object with at least:
- metadata presence
- endpoint reachability
- download success
- format recognition
- parse success
- table extractability

## Completeness Contract

Each browse scope or collection run may produce a `CompletenessSummary`.

The summary must be able to express:
- discovered counts
- attempted counts
- successful counts
- failed counts
- missing counts
- unsupported counts
- table-loadable counts

## Missing Resource Record

Missing or broken resources should remain identifiable over time by:
- `resource_id` when available
- parent dataset and organization identifiers
- last known reason
- last observed timestamp
- repeated-failure count when known

## Acceptance Checks

- visibility and quality are separate concerns
- unsupported resources can still be downloaded and reported
- partial metadata does not prevent inclusion in quality reporting

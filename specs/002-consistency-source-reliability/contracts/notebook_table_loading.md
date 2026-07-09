# Contract: Notebook and Table Loading

## Functions

### `select_and_sample(selection, sample_size=100, formats=None)`

Returns:
- selected `ResourceSummary`
- `TableLoadResult`

### `download_ui(selection, dest, sample_size=0, formats=None)`

Returns:
- `DownloadManifest`
- optional preview results keyed by `resource_id`

### `sample_and_load(resource_ref, sample_size=100, format_hint=None)`

Returns:
- `TableLoadResult`

## Behavior

- supported tabular resources produce table-like results
- unsupported or non-tabular resources return metadata plus structured reasons
- local-file loads and remote samples use the same resource vocabulary where possible
- notebook results do not invent alternate status terminology

## Acceptance Checks

- successful download does not imply successful table load
- unsupported resources remain accessible as files
- notebook previews align with manifest and health reporting language

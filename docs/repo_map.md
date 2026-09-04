## open_ksa repo map

### Purpose

`open_ksa` is a Python library for discovering organizations and datasets from the KSA open data portal, downloading dataset resources to disk, and exposing a newer notebook/CLI API for interactive exploration.

### Current package shape

- `open_ksa/__init__.py`
  - Re-exports the legacy downloader functions.
  - Exposes `cli` as a callable proxy to `download_cli()`.
- `open_ksa/organizations.py`
  - Calls the organizations listing endpoint.
  - Can print a table or write raw results to JSON/CSV.
- `open_ksa/get_org_resources.py`
  - Fetches one organization and extracts `organization_name`, `organization_id`, and `dataset_ids`.
- `open_ksa/get_dataset_resource.py`
  - Core legacy downloader for one dataset.
  - Filters by extension, retries with a portal-specific download URL first, then falls back to the original URL.
- `open_ksa/get_dataset_resources.py`
  - Thin concurrent wrapper over `get_dataset_resource()`.
- `open_ksa/download_file.py`
  - Low-level GET + write helper with "missing.json" bookkeeping.
- `open_ksa/ssl_adapter.py`
  - Shared `requests.Session` with a custom SSL adapter.
- `open_ksa/downloader.py`
  - Newer contract-driven orchestration layer.
  - Contains `fetch_and_load()`, large-file helpers, `sample_and_load()`, and a placeholder `browse()`.
- `open_ksa/notebook.py`
  - Notebook-friendly browse helpers and `download_ui()`.
  - Mostly thin wrappers or placeholders.
- `open_ksa/reader_adapters.py`
  - CSV and JSON readers implemented.
  - Excel reader is still a stub.
- `open_ksa/models.py`
  - Dataclass definitions for the intended public data model.
- `open_ksa/manifest.py`
  - Writes manifest JSON.

### Architectural layers

1. Portal access
   - `organizations.py`
   - `get_org_resources.py`
   - `get_dataset_resource.py`
   - `ssl_adapter.py`

2. File transfer and local persistence
   - `download_file.py`
   - `download_helpers.py`
   - parts of `get_dataset_resource.py`

3. Higher-level user API
   - `downloader.py`
   - `notebook.py`
   - `cli.py`

4. Intended contracts and models
   - `models.py`
   - `specs/001-create-an-extensible/*`
   - `open_ksa/tests/contract/*`

### Main execution flows

#### Legacy bulk download flow

`organizations()` -> `get_org_resources()` -> `get_dataset_resources()` -> `get_dataset_resource()` -> `download_file()`

This is the most real implementation path in the repo today.

#### New programmatic flow

`cli.download_cli()` or `notebook.download_ui()` -> `downloader.fetch_and_load()` -> legacy functions above

This newer layer exists, but only part of the spec is implemented.

### Test layout

- `open_ksa/tests/unit`
  - Mostly API shape and adapter behavior.
- `open_ksa/tests/contract`
  - Verifies that the new downloader/notebook/CLI surface exists.
- `open_ksa/tests/integration`
  - A mix of mocked flows and partially real behavior.

### Important implementation reality

- The repo has two overlapping designs:
  - a working legacy downloader centered on direct `requests` calls.
  - a newer "extensible downloader/notebook/CLI" design described in `specs/001-create-an-extensible/`.

- The tests mostly assert surface existence and basic types.
  - They do not yet prove the full contract described in the spec.

- The spec is aspirational relative to the code.
  - `browse()` (in `downloader.py`) is unimplemented -- distinct from `cli.browse_cli()` below.
  - `cli.browse_cli()` is implemented: wires `notebook.browse_organizations`/
    `notebook.browse_datasets` into a search-organization -> pick-dataset -> download flow,
    with no organization ID needed up front. Live-verified end to end.
  - `list_resources()` returns synthetic placeholder data.
  - `select_and_sample()` does not sample yet.
  - `ExcelAdapter.read_file()` is unimplemented.
  - large-file prompting exists only as helper logic, not as end-to-end behavior.

### Key findings from the current codebase

1. The real production logic still lives in the older module set.
   - If you need dependable behavior today, start with `get_org_resources()` and `get_dataset_resource()`.

2. The new `downloader.fetch_and_load()` is a compatibility/orchestration layer, not yet a full source of truth.
   - It summarizes per dataset, not per resource.
   - It scans the destination directory for any CSV when sampling, which can associate the wrong file to a dataset if multiple downloads share a destination.

3. Several public APIs degrade silently on failure.
   - `cli.download_cli()` catches all exceptions and returns a demo manifest.
   - `downloader.fetch_and_load()` swallows many exceptions and keeps going.
   - This makes the package friendlier for demos but harder to trust operationally.

4. Network and presentation concerns are mixed together.
   - `organizations()` both fetches data and prints a formatted table.
   - Several functions write to disk directly instead of returning structured data plus explicit side effects.

5. Manifest/data model alignment is incomplete.
   - Dataclasses in `models.py` are not used by the downloader path.
   - Manifest entries in `downloader.py` do not match the richer contract from the spec.

6. The test suite appears partially nondeterministic.
   - A full `pytest -q` run did not complete promptly in this environment.
   - A trimmed run also stalled after the initial fast tests, which suggests some tests still rely on live network or slow external behavior.

### Recommended re-entry points for the next review

If the goal is implementation work:
- Start with `open_ksa/downloader.py`
- Then compare against `specs/001-create-an-extensible/contracts/download_api.md`
- Then check `open_ksa/notebook.py` and `open_ksa/cli.py`

If the goal is reliability work:
- Start with `open_ksa/get_dataset_resource.py`
- Then `open_ksa/download_file.py`
- Then isolate live-network behavior behind mocks in tests

If the goal is cleanup/refactor work:
- Unify around one public downloader path.
- Separate network retrieval from console output and filesystem writes.
- Either adopt dataclass models end-to-end or drop them from the public story.

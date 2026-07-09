# Tasks: Create an extensible dataset download and interactive notebook loader

**Input**: Design documents from `/specs/001-create-an-extensible/`  
**Prerequisites**: plan.md, research.md, data-model.md, contracts/

## Execution Flow (main)
```
Follow `.specify/templates/tasks-template.md` rules: setup, TDD tests, core implementation, integration, polish.
```

## Phase 3.1: Setup
- [X] T001 Initialize project dev environment and add dependencies (fail-safe): add `requests` and `pytest` to `pyproject.toml` and `requirements.txt` if present. Files: `/Users/EVA/Desktop/eva/03_development/_dev/libs/py/open_ksa/pyproject.toml`, `/Users/EVA/Desktop/eva/03_development/_dev/libs/py/open_ksa/requirements.txt`.
- [X] T002 [P] Configure linting and formatting (ruff, black) and add dev dependencies in `pyproject.toml`. File: `/Users/EVA/Desktop/eva/03_development/_dev/libs/py/open_ksa/pyproject.toml`.
- [X] T003 [P] Add optional extras for data helpers: `[extras]` `pandas` and `numpy` in `pyproject.toml`.

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE IMPLEMENTATION

### Contract tests (one per contract file) — create failing tests
- [X] T004 [P] Create failing contract test for download API signature: `open_ksa/tests/contract/test_download_api_contract.py`. Test should import `open_ksa.downloader` and assert `fetch_and_load` exists and raises NotImplementedError or is unimplemented.
- [X] T005 [P] Create failing contract test for notebook API signature: `open_ksa/tests/contract/test_notebook_api_contract.py`. Test should import `open_ksa.downloader` and assert `browse` exists and raises NotImplementedError or is unimplemented.

### Data-model tests (one per entity)
- [X] T006 [P] Create failing unit tests for `Organization` model in `open_ksa/tests/unit/test_models_organization.py` asserting required fields.
- [X] T007 [P] Create failing unit tests for `Dataset` model in `open_ksa/tests/unit/test_models_dataset.py`.
- [X] T008 [P] Create failing unit tests for `Resource` model in `open_ksa/tests/unit/test_models_resource.py`.
- [X] T009 [P] Create failing unit tests for `DownloadManifest` model in `open_ksa/tests/unit/test_models_manifest.py`.
- [X] T010 [P] Create failing unit tests for `ReaderAdapter` interface in `open_ksa/tests/unit/test_reader_adapter.py`.

### Integration / user story tests
- [X] T011 [P] Create integration-style test simulating a notebook flow: `open_ksa/tests/integration/test_notebook_quickstart.py`. This should use the `quickstart.md` scenario and assert high-level calls exist (browse, fetch_and_load) and that when mocked responses are provided, manifest entries are produced.
- [X] T012 [P] Create test for streaming-sample behavior: `open_ksa/tests/integration/test_streaming_sample.py`. Mock HTTP endpoint streaming CSV, assert `sample_and_load(sample_size=N)` returns N rows without full file save.
- [X] T013 [P] Create test for large-file prompting/auto-save: `open_ksa/tests/integration/test_on_disk_prompt.py`. Simulate Content-Length > threshold and assert interactive prompt behavior (mock input) and non-interactive auto-save.

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [X] T014 Implement `open_ksa/models.py` and add `Organization`, `Dataset`, `Resource`, `DownloadManifest` dataclasses. File: `/Users/EVA/Desktop/eva/03_development/_dev/libs/py/open_ksa/open_ksa/models.py`.
- [X] T015 Implement `open_ksa/reader_adapters.py` with `CSVAdapter`, `JSONAdapter`, `ExcelAdapter` interfaces and initial stubs. File: `/Users/EVA/Desktop/eva/03_development/_dev/libs/py/open_ksa/open_ksa/reader_adapters.py`.
- [X] T016 Implement `open_ksa/download_helpers.py` utilities: atomic file writes, retries, streaming helpers (stop-after-N rows). File: `/Users/EVA/Desktop/eva/03_development/_dev/libs/py/open_ksa/open_ksa/download_helpers.py`.
- [X] T017 Implement core `downloader` module with API surface: `open_ksa/downloader.py` (module at `/Users/EVA/Desktop/eva/03_development/_dev/libs/py/open_ksa/open_ksa/downloader.py`) exposing `fetch_and_load` and `browse` functions (raise NotImplementedError initially until behavior added incrementally).
- [X] T018 Implement on-disk threshold config and prompt logic in downloader. Update `open_ksa/config.py` or add constants in `open_ksa/downloader.py`.

## Phase 3.4: Integration
- [X] T019 [P] Hook reader adapters into `downloader.fetch_and_load` to parse supported formats into pandas.DataFrame when `sample_size>0` and `pandas` is installed. File: `/Users/EVA/Desktop/eva/03_development/_dev/libs/py/open_ksa/open_ksa/downloader.py` and `/Users/EVA/Desktop/eva/03_development/_dev/libs/py/open_ksa/open_ksa/reader_adapters.py`.
- [X] T020 Implement CLI entrypoint `open_ksa/cli.py` and add console_script entry in `pyproject.toml`. CLI should provide `browse` and `download` subcommands with NLTK-style prompts.
- [X] T021 Implement `manifest` creation and writing to disk after operations. File: `/Users/EVA/Desktop/eva/03_development/_dev/libs/py/open_ksa/open_ksa/manifest.py`.
- [X] T022 Add progress reporting with `tqdm` (optional) and safe cancellation handling (KeyboardInterrupt) in `downloader`.

## Phase 3.5: Polish
- [X] T023 [P] Add unit tests for validation and helpers in `open_ksa/tests/unit/` (validation functions, atomic writes, retry logic).  
- [X] T024 [P] Document quickstart and add `examples/scripts/` demo matching `quickstart.md` and add a Jupyter workbook in `examples/workbooks/` demonstrating browsing and sample loading.
- [X] T025 [P] Add README snippets and update `open_ksa/__init__.py` to expose top-level convenience functions.
- [X] T026 Run linter and formatter fixes and ensure no linter errors remain.

## Phase 3.6: Notebook Contracts & Traversal (NEW)
- [X] T027 [P] Create contract tests for `browse_organizations` in `open_ksa/tests/contract/test_browse_contract.py`. Assert function exists and returns list of org metadata (UUIDs present) and supports interactive selection via mocked input.
- [X] T028 [P] Create contract tests for `browse_datasets` in `open_ksa/tests/contract/test_browse_contract.py`. Assert function exists, returns dataset metadata with `dataset_id` (UUID), and supports interactive selection.
- [X] T029 [P] Create contract tests for `list_resources` in `open_ksa/tests/contract/test_browse_contract.py`. Assert resource metadata includes `resource_id` (UUID), `url`, and `format`.
- [X] T030 [P] Create contract test for `select_and_sample` in `open_ksa/tests/contract/test_browse_contract.py` that asserts when given UUIDs returns resource metadata and a sample (DataFrame or list) when `sample_size>0`.
- [X] T031 Implement `open_ksa/notebook.py` with stubs for `browse_organizations`, `browse_datasets`, `list_resources`, `select_and_sample`, and `download_ui` that raise NotImplementedError until behavior is added incrementally. File: `/Users/EVA/Desktop/eva/03_development/_dev/libs/py/open_ksa/open_ksa/notebook.py`.
- [X] T032 [P] Integration test for notebook traversal flow: `open_ksa/tests/integration/test_notebook_traversal.py` - simulate interactive selection (monkeypatch `input`) and assert correct UUIDs are returned and `select_and_sample` returns expected sample (mocked `reader_adapters`).

## Phase 3.7: Implement bulk downloader (fetch_and_load)
The CLI currently delegates to `downloader.fetch_and_load` which remains a stub. Implementing the full bulk download is the next priority.

- T033 Implement contract tests for `fetch_and_load` in `open_ksa/tests/contract/test_download_api_contract.py` expanding assertions to cover manifest schema, data_map keys, and error reporting. Mark as [P].
- T034 [P] Implement unit tests for manifest writer behavior and manifest schema validation in `open_ksa/tests/unit/test_manifest.py`.
- T035 Implement `open_ksa/downloader.fetch_and_load` core behavior (streaming sampling, bulk download, validation, concurrent downloads, manifest creation). File: `/Users/EVA/Desktop/eva/03_development/_dev/libs/py/open_ksa/open_ksa/downloader.py`.
- T036 Implement per-resource validation helpers and retry/backoff in `open_ksa/download_helpers.py` (resume, HTTP range support where available). Update tests accordingly.
- T037 [P] Implement integration tests that mock network responses for success, redirect, HTML placeholder, large-file Content-Length, and assert manifest and data_map outcomes: `open_ksa/tests/integration/test_fetch_and_load.py`.
- T038 Update CLI to gracefully fallback to a built-in demo when `fetch_and_load` is not implemented or network unavailable (safe demo mode). File: `open_ksa/cli.py`.

## Dependencies and Parallelization (updated)
- Implementation tasks: T035 must follow T033/T034 (tests-first). T036 is a helper for T035 and can be worked on in parallel but must be completed before integration tests T037.


## Dependencies and Parallelization
- Parallelizable [P] tasks: T002, T003, T004-T013 (tests for separate files), T019, T023-T025.  
- Sequential tasks (no [P]): T001 -> tests (T004...) must be created before implementation tasks T014-T018.

# New parallel group: T027-T030 (contract tests) can be created in parallel and run independently.
# Notebook implementation (T031) should be done after those contract tests exist so implementation follows TDD.

## Example parallel execution commands
```
# Launch contract & data-model tests in parallel
pytest open_ksa/tests/contract/test_download_api_contract.py &
pytest open_ksa/tests/unit/test_models_organization.py &
pytest open_ksa/tests/integration/test_streaming_sample.py &
wait
```

## Validation Checklist (must be satisfied by /tasks run)
- [ ] All contract files have contract tests (T004-T005)
- [ ] All entities from data-model.md have model tasks/tests (T006-T010)
- [ ] Integration tests for user stories exist (T011-T013)
- [ ] Tests fail before implementation begins
- [ ] Each implementation task references exact file paths

*** End Tasks***

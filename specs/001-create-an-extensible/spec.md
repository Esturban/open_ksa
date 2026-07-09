# Feature Specification: Create an extensible dataset download and interactive notebook loader

**Feature Branch**: `001-create-an-extensible`  
**Created**: 2025-09-23  
**Status**: Draft  
**Input**: User description: "Create an extensible dataset download and interactive notebook loader: allow users to specify organizations or datasets to bulk-download, filter via fuzzy or typed search, validate downloadable resources (CSV/JSON/Excel), provide reader adapters to load samples into pandas/numpy, and add CLI/Notebook API to browse available datasets interactively. Include fallbacks for non-downloadable resources and support specifying output directories and sample sizes."

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
   → Authors MUST include at least 2 clarifying questions for any ambiguity related to input formats,
     side-effects, or success criteria. These questions must be answered before Phase 1 design proceeds.
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **One-shot functional snippet**: For features involving data transformation or I/O, include a 3–8 line
   functional snippet in the spec demonstrating the minimal API call and its expected return value. This
   snippet will be used by implementers and agents as the authoritative example for early validation.
5. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies  
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
A data scientist or analyst working in a Jupyter notebook (or Python REPL) wants to discover and load open datasets from the `open.data.gov.sa` mirror. They should be able to:
- Browse datasets by organization, or search by keywords (fuzzy or typed).
- Select one or more dataset resources to bulk-download into a user-specified directory.
- Load one or multiple samples directly into the notebook as pandas DataFrames or numpy arrays using lightweight reader adapters.
- Handle cases where a resource is not a valid downloadable data file (e.g., HTML placeholder) via clear fallback behavior.

### Detailed User Stories
- **As a data scientist**, I can open a brand-new Jupyter workbook and query an `organization_id` to retrieve a short list of available datasets and sample counts so I can determine whether I need one or multiple datasets for analysis.
- **As a data analyst**, I can request downloads for a specific organization or dataset resource and have the files saved to a chosen working directory for later exploration.
- **As a data scientist**, I can download multiple datasets into an accessible workspace directory in a single command to prepare for cross-dataset analysis.
- **As a data scientist**, I can load a single dataset sample into memory immediately as a `pandas.DataFrame` for analysis.
- **As a data scientist**, I will receive clear, actionable notifications in the manifest for any resource that failed to download or validate.

### Acceptance Scenarios
1. **Given** a dataset resource that is a CSV and reachable, **When** the user requests a sample (sample_size > 0), **Then** the library streams the remote file and stops after collecting the requested N rows and returns a `pandas.DataFrame` representing the sample.
2. **Given** an organization identifier, **When** the user requests "download all datasets matching query X" with `dest=/tmp/ods`, **Then** the library downloads all valid resources into the directory and returns a manifest summarizing successes and failures.
3. **Given** an interactive CLI or notebook call with no dataset argument, **When** the user invokes the browse command, **Then** the tool lists available datasets and allows the user to pick by index or fuzzy-match, following an NLTK-style download UX (textual prompts and numeric selections).
4. **Given** a resource URL that returns an HTML page instead of a data file, **When** the tool attempts to stream, **Then** it logs the failure, includes the reason in the manifest, and continues downloading other resources.
5. **Given** files that are not excessively large (typical case), **When** the user requests `sample_size`, **Then** streaming-stop-after-N strategy will return only requested rows without downloading the full file to disk.

### Edge Cases
- Resource URL redirects or requires TLS variants that may fail: tool should attempt a safe retry and surface the reason on failure.
- Mixed-format archives (ZIPs containing multiple files): treat as a non-supported resource unless explicitly requested; report as unsupported in the manifest.
- Remote rate-limiting or large organizations: provide partial results and an idempotent manifest for resume.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST allow users to specify either an `organization_id` or a `dataset_id` (or neither) to scope downloads.
- **FR-002**: System MUST provide a `browse()` interactive mode that lists available datasets and supports selection via index or fuzzy string match.
- **FR-003**: System MUST support bulk download of resources returned for a dataset or organization, saving into a user-specified `dest` directory.
- **FR-004**: System MUST provide `sample_and_load()` to return in-memory representations (pandas.DataFrame / numpy) for supported formats: **CSV, JSON, XLS, XLSX**.
- **FR-005**: System MUST validate each resource before saving: confirm Content-Type and/or sample read to ensure it's a parsable data file; if validation fails, report in the manifest and skip loading.
- **FR-006**: System MUST allow users to set `sample_size` (number of rows) and `max_concurrent_downloads` (defaults documented) for bulk operations.
- **FR-007**: System MUST return a download manifest object summarizing per-resource: resource_id, url, local_path (if downloaded), status (success|skipped|failed), and reason (error message or validation reason).
- **FR-008**: System MUST expose a simple CLI entrypoint and a programmatic Notebook API with the same core behaviors. The CLI UX should follow an NLTK-style textual prompt and numeric selection flow.
- **FR-009**: System MUST gracefully handle non-downloadable resources (HTML, auth pages) by skipping and reporting rather than crashing.
- **FR-010**: System MUST include at least one unit test per functional requirement demonstrating expected behavior and failure modes.

- **FR-011**: System MUST prompt the user (interactive) when a resource exceeds `on_disk_threshold_bytes` and offer to stream-save the file to an on-disk `large_files_dir`; in non-interactive mode the file should be saved to `large_files_dir` automatically and reflected in the manifest.

### Non-functional Requirements
- **NFR-001**: Operations MUST be cancellable/interruptible in an interactive environment (e.g., KeyboardInterrupt in notebook) leaving a consistent manifest on disk.
- **NFR-002**: For small-to-medium sized datasets (<= 100MB per resource), default operations should complete within reasonable time on a modern dev workstation; document expectations and provide progress feedback.
- **NFR-003**: Use minimal, widely trusted dependencies; the notebook API should not require heavier dependencies unless optional extras are explicitly installed.
- **NFR-004**: The library MUST provide a configurable default threshold `on_disk_threshold_bytes` (default 100_000_000) and a configurable `large_files_dir` where large resources are saved when on-disk streaming is chosen.

### Testability
Each FR above must be accompanied by unit tests in `open_ksa/tests/` that:
- Mock remote resource responses (CSV, JSON, HTML, redirects) and assert manifest entries and returned DataFrames.
- Validate `sample_size` behavior by returning only requested rows; tests should confirm streaming-stop-after-N behavior.
- Test browse interactive flow in a non-interactive mode by simulating selection input.

## Key Entities *(include if feature involves data)*
- **Organization**: represents provider of datasets; attributes: `organization_id`, `title`, `description`, `dataset_count`.
- **Dataset**: top-level dataset entity; attributes: `dataset_id`, `title`, `resources` (list of Resource metadata).
- **Resource**: downloadable file descriptor; attributes: `resource_id`, `name`, `url`, `format`, `content_type`, `size`.
- **DownloadManifest**: result of a bulk operation; attributes: `timestamp`, `requested_by`, `dest_path`, `entries` where each entry is `{resource_id, url, local_path, status, reason}`.
- **ReaderAdapter**: abstraction that, given a local file path or byte stream and a resource format, returns a `pandas.DataFrame` or `numpy` array. Implementations: `CSVAdapter`, `JSONAdapter`, `ExcelAdapter`.

---

## One-shot functional snippet (authoritative example)
```python
from open_ksa import downloader

# download and load a small sample from an organization using fuzzy query
manifest, data_map = downloader.fetch_and_load(
    organization_id='ministry-of-labor',
    query='job vacancies',
    dest='/tmp/open_ksa',
    sample_size=100,
    formats=['csv','json']
)
# manifest: DownloadManifest
# data_map: dict mapping resource_id -> pandas.DataFrame
```

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
- [ ] Scope is clearly bounded
- [ ] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked where present
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [ ] Review checklist passed

---

## Open Questions / Ambiguities
1. **Default sample fetching strategy**: Resolved — The library will use a streaming-stop-after-N-rows strategy by default for sample fetching.  
2. **Supported formats**: Resolved — The initial supported formats are CSV, JSON, XLS, and XLSX (majority coverage).  
3. **Large-file handling and memory constraints**: Resolved — The library MUST prompt the user and offer on-disk streaming for large files. A configurable `on_disk_threshold_bytes` (default 100_000_000 ≈ 100MB) will determine when to suggest on-disk saving. If a resource's `Content-Length` exceeds the threshold (or streaming detects large size), the tool will prompt in interactive mode and automatically save to a configured `large_files_dir` in non-interactive/batch mode.
4. **Authentication & private datasets**: Resolved — Initial scope includes only public, unauthenticated endpoints.
5. **CLI interactivity UX**: Resolved — The interactive CLI will follow an NLTK-style textual prompt and numeric selection flow (no GUI widgets).

---

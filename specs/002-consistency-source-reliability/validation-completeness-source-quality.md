# Capability Spec 3: Validation, Completeness, and Source Quality

## Purpose

Define how `open_ksa` handles unreliable endpoints, mixed file quality, and incomplete metadata without losing coverage.

## User Intent

Users need to know:
- what was visible from the source system
- what the library could actually retrieve
- what appears broken or missing
- what may still require manual inspection on the portal

## Quality Philosophy

This capability is capture-first and report-first.

It does not assume the source portal is consistently correct.
It does not assume metadata and download endpoints agree.
It does not assume every downloaded file is parseable or table-loadable.

## Functional Requirements

- **VQ-001**: The system MUST preserve visibility of resources even when they fail validation.
- **VQ-002**: The system MUST represent resource health as multiple dimensions rather than a single pass/fail flag.
- **VQ-003**: The system MUST differentiate between endpoint reachability, metadata presence, download success, format recognition, parse success, and table extractability.
- **VQ-004**: The system MUST produce completeness summaries at organization, dataset, and run levels.
- **VQ-005**: The system MUST persist records of missing, broken, or repeatedly failing resources.
- **VQ-006**: The system MUST support mixed resource types including tabular, semi-structured, text, and unknown files.
- **VQ-007**: The system MUST allow unsupported resources to remain downloadable and reportable when possible.
- **VQ-008**: The system MUST clearly distinguish "visible in navigation" from "suitable for notebook table loading."

## Health Dimensions

Each resource should be classifiable across:
- metadata present
- endpoint reachable
- downloadable
- recognized format
- parseable
- table extractable

None of these dimensions implies the others automatically.

## Completeness Reporting

Completeness reporting should summarize:
- how much of the source tree was discovered
- how much was attempted
- how much was downloaded
- how much failed
- how much remains missing
- how much is unsupported for table loading

## Acceptance Scenarios

1. **Given** a dataset lists five resources, **When** only three download successfully, **Then** completeness reporting still shows all five discovered resources and distinguishes the two failures.
2. **Given** a download endpoint returns HTML or an empty body, **When** validation runs, **Then** the resource remains visible, is marked failed or unparseable, and contributes to completeness stats.
3. **Given** a text or unknown-format file downloads successfully, **When** the run completes, **Then** it remains in the manifest as downloaded but not table-loadable by default.
4. **Given** a resource fails repeatedly across runs, **When** users inspect quality data, **Then** the resource can be identified as a repeated failure rather than a one-off issue.
5. **Given** portal metadata is missing or inconsistent, **When** resources are listed, **Then** the system still produces resource summaries with partial metadata and explicit unknowns.

## Explicit Defaults

- Validation informs; it does not hide.
- Unsupported does not mean discard.
- Missing and failed resources contribute to completeness accounting.
- Quality stats are user-visible, not operator-only.

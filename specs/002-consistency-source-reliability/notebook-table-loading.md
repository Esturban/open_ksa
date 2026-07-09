# Capability Spec 4: Notebook and Table Loading

## Purpose

Define how collected resources become notebook-friendly tables without misrepresenting non-tabular resources as if they were tables.

## User Intent

Users want to move from discovery and download into analysis quickly. When a resource is tabular and supported, they want a table-like object. When it is not, they still want the file and a clear reason why no table was produced.

## Core Behavior

- Notebook usage remains downstream of organization-first discovery and selection.
- Notebook helpers share the same manifest and quality vocabulary as collection workflows.
- Table loading is a supported capability for tabular resources, not a universal promise for every file.

## Functional Requirements

- **NT-001**: The system MUST support loading supported tabular resources into notebook-friendly tables.
- **NT-002**: The system MUST support resource sampling for notebook exploration.
- **NT-003**: The system MUST produce structured non-table results for unsupported or non-tabular resources.
- **NT-004**: The system MUST support local-file loading for already downloaded resources.
- **NT-005**: The system MUST allow remote sampling behavior where the resource type and size make it practical.
- **NT-006**: The system MUST use the same resource identifiers and status vocabulary used by browse and download flows.
- **NT-007**: The system MUST not imply that successful download automatically means successful table extraction.
- **NT-008**: The system MUST report why a table was not produced when loading fails or is unsupported.

## Supported Notebook Outcomes

For a selected resource, notebook flows should end in one of these outcomes:
- table loaded successfully
- sample loaded successfully
- file available but not table-loadable
- load attempt failed with reason

## Acceptance Scenarios

1. **Given** a CSV resource downloads successfully, **When** the user requests a notebook sample, **Then** the system returns a table-like result and records that it was sampled.
2. **Given** an XLSX resource is supported, **When** the user loads it from disk, **Then** the system returns a table-like result without redefining its resource identity.
3. **Given** a text file downloads successfully, **When** the user asks for a table, **Then** the system returns metadata plus a structured reason that the file is not table-loadable by default.
4. **Given** a resource is downloadable but unparseable, **When** notebook loading is attempted, **Then** the system reports a failed table-load result rather than treating the resource as missing.
5. **Given** a user already selected a resource in discovery mode, **When** they transition to notebook loading, **Then** no alternate identifier or vocabulary is required.

## Explicit Defaults

- Table-first for supported tabular formats.
- Non-tabular resources stay accessible as files plus metadata.
- Notebook helpers inherit the reliability and completeness rules from the other specs.

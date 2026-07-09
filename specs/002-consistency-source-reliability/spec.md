# Feature Specification: Consistency and source-reliable collection for `open_ksa`

**Feature Branch**: `002-consistency-source-reliability`  
**Created**: 2026-03-09  
**Status**: Draft  
**Input**: User description: "Draft the specs for consistency and source reliability so the library can keep collecting from the KSA portal despite broken endpoints, inconsistent files, and partial metadata, while staying organization-first and notebook-friendly."

## Summary

This spec family defines how `open_ksa` should behave when the source system is incomplete, partially broken, or inconsistent. The goal is not to reject imperfect data sources. The goal is to collect as much useful material as possible, make selection/navigation consistent, and report clearly what was discovered, what was downloaded, what failed, and what remains missing.

The canonical workflow remains organization-first:
- browse organizations
- inspect datasets within an organization
- inspect resources within a dataset
- download at organization, dataset, or resource scope
- load supported resources into notebook-friendly tables

The spec family is split into four capability areas:
1. Discovery and navigation
2. Batch download and orchestration
3. Validation, completeness, and source quality
4. Notebook and table loading

All four areas share one vocabulary for selection, resource status, manifest entries, and completeness reporting.

## Primary User Story

A data analyst or researcher wants to collect public data from the KSA open data portal even when the portal is inconsistent. They need to browse by organization, decide what is worth collecting, download whole organizations or smaller subsets, and understand what was successfully captured versus what is broken, unsupported, or missing.

## Product Principles

- Organization-first navigation is the default path.
- Collection is best-effort, not strict-only-valid.
- Broken sources remain visible unless explicitly filtered out.
- Validation informs users; it does not silently hide data.
- The same selection and status concepts must apply across Python API, CLI, and notebook helpers.
- Notebook loading is table-first for supported tabular resources, but non-tabular resources must still remain discoverable and downloadable.

## Shared Functional Requirements

- **FR-001**: The system MUST support organization, dataset, and resource selection scopes.
- **FR-002**: The system MUST treat organization browsing as the canonical entry point.
- **FR-003**: The system MUST preserve visibility of broken, missing, unsupported, or partially valid resources in browse and reporting flows.
- **FR-004**: The system MUST use a consistent status vocabulary for discovery, download, validation, and notebook loading flows.
- **FR-005**: The system MUST produce per-resource manifests and per-scope completeness summaries.
- **FR-006**: The system MUST keep collection best-effort: failure of one resource MUST NOT abort the wider batch by default.
- **FR-007**: The system MUST distinguish between a resource being visible, downloadable, parseable, and table-loadable.
- **FR-008**: The system MUST support table-style notebook loading for supported tabular formats while retaining non-tabular files as downloadable resources.

## Non-Functional Requirements

- **NFR-001**: Specifications MUST be decision-complete enough for a junior engineer or coding agent to implement without choosing product semantics.
- **NFR-002**: Specifications MUST assume normal operation includes broken endpoints, missing metadata, empty files, redirects, and unsupported formats.
- **NFR-003**: Specifications MUST favor transparency and reproducibility over silent fallback behavior.
- **NFR-004**: Specifications MUST remain compatible with the repo’s current “collect as much as possible” behavior while defining a stricter reporting model.

## Deliverables

This feature package contains:
- capability spec for discovery and navigation
- capability spec for batch download and orchestration
- capability spec for validation, completeness, and source quality
- capability spec for notebook and table loading
- shared data model
- shared contracts
- cross-spec consistency matrix

## Acceptance Criteria

1. A junior implementer can read the spec package and know the canonical workflow, status model, and reporting expectations without inferring missing product decisions.
2. The spec package clearly defines how broken or partial portal data should appear in browse, download, and notebook flows.
3. The spec package defines one shared vocabulary for selection requests, resource summaries, health states, manifests, and completeness summaries.
4. The spec package defines how organization-first collection remains the primary workflow even when users later narrow to datasets or resources.
5. The spec package is documentation-only and does not require code changes to be useful as planning input.

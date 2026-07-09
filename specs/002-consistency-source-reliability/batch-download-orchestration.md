# Capability Spec 2: Batch Download and Orchestration

## Purpose

Define one canonical collection workflow that can download at organization, dataset, or resource scope while preserving best-effort behavior and precise reporting.

## User Intent

Users want to collect large portions of the portal without manually stepping through each endpoint, but they still need a trustworthy record of what was attempted, what succeeded, and what failed.

## Core Behavior

- One orchestration flow is the source of truth for collection.
- The orchestration flow accepts the same selection model used in discovery.
- Resource-level results are always recorded, even when the user requested a larger scope.

## Functional Requirements

- **BD-001**: The system MUST support organization, dataset, and resource batch scopes.
- **BD-002**: The system MUST treat one orchestration API as the canonical collection path used by all user surfaces.
- **BD-003**: The system MUST record one manifest entry per resource, not only per dataset or per run.
- **BD-004**: The system MUST continue attempting later resources after individual resource failures by default.
- **BD-005**: The system MUST distinguish between discovered, attempted, downloaded, skipped, failed, and missing resource outcomes.
- **BD-006**: The system MUST support idempotent re-runs so already valid downloads are not duplicated unnecessarily.
- **BD-007**: The system MUST produce destination layouts that remain interpretable at organization, dataset, and resource scope.
- **BD-008**: The system MUST make completeness summaries available for the run as a whole.

## Destination Layout Rules

The spec does not require a specific implementation path layout, but it does require:
- organization batches remain attributable to the originating organization
- dataset batches remain attributable to the originating dataset
- single-resource downloads remain attributable to the resource and dataset they came from
- manifests and files can be reconciled later without ambiguous ownership

## Acceptance Scenarios

1. **Given** a user selects an organization, **When** a batch run is executed, **Then** all discovered eligible resources are attempted and the manifest records each resource separately.
2. **Given** some resources fail mid-run, **When** the rest are still reachable, **Then** the run completes and the manifest contains both failures and successes.
3. **Given** a user reruns the same organization batch, **When** previously valid files are already present, **Then** the system avoids duplicate work and still records the run consistently.
4. **Given** a user selects only two resources from one dataset, **When** the batch runs, **Then** only those resource IDs are attempted and reported.
5. **Given** a resource was discovered but never attempted due to scope or filtering, **When** the manifest is inspected, **Then** it is not mislabeled as a download failure.

## Explicit Defaults

- Per-resource manifests are mandatory.
- Best-effort is the default batch mode.
- The canonical orchestrator is the public source of truth.
- Narrower user surfaces must adapt to the orchestrator, not redefine its semantics.

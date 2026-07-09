# Capability Spec 1: Discovery and Navigation

## Purpose

Define how users find and select sources while keeping the workflow organization-first and resilient to weak portal search and inconsistent metadata.

## User Intent

Users want to answer:
- which organizations contain relevant data
- which datasets exist under that organization
- which resources are actually present
- which sources are likely collectible versus already known to be broken, missing, or unsupported

## Canonical Workflow

1. Browse organizations.
2. Select one organization.
3. Browse datasets within that organization.
4. Inspect resources within a dataset.
5. Select one of three scopes:
   - whole organization
   - selected datasets
   - selected resources

## Functional Requirements

- **DN-001**: The system MUST present organizations as the primary discovery root.
- **DN-002**: The system MUST support browsing datasets within a selected organization.
- **DN-003**: The system MUST support listing resources within a selected dataset.
- **DN-004**: The system MUST surface summary stats during navigation, including discovered counts and known quality indicators.
- **DN-005**: The system MUST support local or overlay query filtering as a secondary aid without depending on portal-side search reliability.
- **DN-006**: The system MUST keep broken, missing, unsupported, or previously failed resources visible by default.
- **DN-007**: The system MUST allow users to select at organization, dataset, or resource scope.
- **DN-008**: The system MUST use the same identifiers later used by download and notebook flows.

## Summary Stats Visible During Browse

At minimum, the navigation layer should be able to surface:
- datasets discovered
- resources discovered
- resources with known download success
- resources with known download failure
- resources marked missing
- resources with unsupported or unknown format

These are guidance signals, not hard filters.

## Acceptance Scenarios

1. **Given** an organization with incomplete metadata, **When** the user browses it, **Then** datasets and resources remain visible with missing fields tolerated and summary stats still produced.
2. **Given** weak or broken portal-side search, **When** the user filters results, **Then** local/overlay filtering still narrows the visible organization, dataset, or resource set.
3. **Given** resources with known prior failures, **When** a dataset is listed, **Then** those resources remain visible with failure status markers instead of being hidden.
4. **Given** a user wants the entire organization, **When** they select at organization scope, **Then** the selection object represents the organization without forcing dataset-by-dataset selection.
5. **Given** a user wants only specific files, **When** they inspect a dataset’s resources, **Then** they can select one or more resource identifiers directly.

## Explicit Defaults

- Search is secondary.
- Organization-first is primary.
- Resource visibility is broader than resource validity.
- Summary stats are informational and do not remove resources from view.

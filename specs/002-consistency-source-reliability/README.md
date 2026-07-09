# `002-consistency-source-reliability`

This spec package defines the documentation-only target for making `open_ksa` more consistent and more reliable against an inconsistent source portal.

Contents:
- [spec.md](./spec.md): umbrella specification and shared requirements
- [data-model.md](./data-model.md): shared entities and status vocabulary
- [consistency-matrix.md](./consistency-matrix.md): cross-surface invariants
- [discovery-navigation.md](./discovery-navigation.md): organization-first browsing and selection
- [batch-download-orchestration.md](./batch-download-orchestration.md): canonical collection workflow
- [validation-completeness-source-quality.md](./validation-completeness-source-quality.md): quality and completeness rules
- [notebook-table-loading.md](./notebook-table-loading.md): notebook-facing table behavior
- [contracts/](./contracts): shared product contracts for each capability area

Scope notes:
- This package is draft-spec only.
- It does not implement code.
- It is intended to replace ad hoc interpretation with a single vocabulary for selection, reliability, and completeness.

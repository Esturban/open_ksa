# Consistency Matrix

This matrix defines behaviors that must remain consistent across the Python API, notebook helpers, and CLI-facing workflows.

| Concern | Discovery | Batch download | Notebook loading | Shared rule |
|---|---|---|---|---|
| Entry point | Organization-first | Accept org/dataset/resource selections | Reuse org-first browse helpers | Org-first is canonical |
| Selection vocabulary | `SelectionRequest` | `SelectionRequest` | `SelectionRequest` or equivalent | Same scope names everywhere |
| Resource visibility | Broken resources still shown | Broken resources still attempted when selected | Broken resources shown with reasons | Visibility is not the same as validity |
| Status terms | `ResourceHealth` and summaries | `ManifestEntry` and summaries | `TableLoadResult` plus health | Same status names and meanings |
| Failure behavior | Report and continue browsing | Report and continue batch | Report and return metadata plus reason | Do not silently hide failures |
| Completeness stats | Visible pre-download | Visible post-download | Visible when loading tables | Same counters and meanings |
| Unsupported formats | Visible and selectable | Download if possible | Not table-loaded by default | Unsupported is not hidden |
| Search/filter | Secondary overlay | Secondary filter on selected scope | Secondary convenience | Correctness does not depend on portal search |

## Mandatory cross-surface guarantees

- A resource selected in browse flows must be addressable by the same identifier in download and notebook flows.
- The manifest vocabulary must not conflict with browse summary vocabulary.
- A user must be able to explain any resource outcome using the same three lenses:
  - downloadability
  - parseability
  - table-loadability
- A partially broken organization must remain collectible at the organization level.

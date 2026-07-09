# notebook_api

This document specifies the notebook-facing API contract and expected ergonomics for interactive discovery and sampling of datasets inside Jupyter or interactive Python shells. It mirrors the `download_api` but focuses on in-memory, exploratory usage.

Primary functions

- `browse_organizations(query: Optional[str]=None, limit: int=20) -> List[Dict]`
  - Returns a list of organization metadata dicts (each includes `organization_id` (UUID), `title`, `description`, `dataset_count`).
  - When called with no args and `interactive=True`, this should display an NLTK-style textual menu: a short numbered list and a prompt `Downloader>` where the user types an index or `q` to quit. The function should return the selected `organization_id` when a numeric selection is made.

- `browse_datasets(organization_id: str, query: Optional[str]=None, limit: int=20, interactive: bool=True) -> List[Dict]`
  - Lists datasets for a given organization. Each dataset dict must include `dataset_id` (UUID), `title`, `description`, and `resource_count`.
  - In interactive mode, the function should show a numbered list and return the chosen `dataset_id`.

- `list_resources(dataset_id: str) -> List[Dict]`
  - Returns a list of resource metadata for the dataset. Each resource must include `resource_id` (UUID), `name`, `url`, `format`, `size` (if known).
  - This supports UUID-based selection: callers and UIs should always use the `resource_id` to refer to a resource (not filename or human title).

- `select_and_sample(organization_id: Optional[str]=None, dataset_id: Optional[str]=None, resource_id: Optional[str]=None, sample_size: int=100, interactive: bool=True) -> Tuple[Dict, Optional[pandas.DataFrame]]`
  - High-level helper that guides the user through organization → dataset → resource selection (NLTK-style) when IDs are omitted. If IDs are provided, it skips selection and proceeds.
  - Returns `(resource_metadata_dict, sample_df_or_none)` where `sample_df_or_none` is a pandas.DataFrame if the resource is supported and sample_size>0, otherwise None.

- `download_ui(organization_id: Optional[str] = None, dataset_id: Optional[str] = None, dest: str = '.', sample_size: int = 0, interactive: bool=True)`
  - Notebook convenience wrapper that calls `fetch_and_load` under the hood but returns a short, notebook-friendly summary (manifest + small preview DataFrames) and displays progress/messages inline. When called without IDs and `interactive=True`, it should use `browse_organizations` and `browse_datasets` to guide selection.

NLTK-style UX parallels

- The browsing helpers should implement the same textual layout and prompt semantics shown in `nltk.download()`:
  - Top-level menu header, a short list of choices (index + human title + counts), and prompt `Downloader>` for numeric input.
  - Support short commands: numeric index to select, `l` to list more, `q` to quit, `d` to download directly, and `h` for help (mirroring NLTK labels). Keep the command set minimal (see Quick UX below).
- Interactive prompts MUST be opt-in: `interactive=True` to show prompts in notebook cells; otherwise return structured results for programmatic consumption.

Quick UX example (textual):

```
NLTK Downloader
+----------------------------------------
 1) Ministry of Labor (34 datasets)
 2) Ministry of Health (120 datasets)
 3) King Saud University (216 datasets)
 Enter choice or `q` to quit: 1
```

After selecting an organization, the datasets list is shown similarly; choosing a dataset shows resources, each with `resource_id` (UUID) shown alongside a short index and the user can type a resource index to sample or `d` to download the resource.

Examples (notebook)

```python
from open_ksa import browse, sample_and_load, download_ui

# Discover datasets
candidates = browse(query='job vacancies')  # returns list of dicts
# Show the first few
candidates[:5]

# Sample a remote resource locally (if path or URL)
df = sample_and_load('path/to/file.csv', nrows=50)
df.head()

# Notebook-friendly bulk download
manifest, previews = download_ui(organization_id='ministry-of-labor', sample_size=100)
# previews: mapping resource_id -> small DataFrame
```

Testing guidance

- Tests should cover both programmatic and interactive modes:
  - Programmatic: call `browse_organizations` / `browse_datasets` / `list_resources` with mocks and assert return values (UUIDs, counts, metadata).
  - Interactive: simulate user input (monkeypatch `input()` or the prompt helper) and assert selection flow returns expected UUIDs.
- `select_and_sample` tests should verify that when provided UUIDs it skips interactive selection, and when omitted it prompts and returns the intended resource metadata and sample DataFrame.
- Notebook quickstart should include a small cached sample and a recorded fixture for network calls.

Notes

- Organizations, datasets, and resources are identified by UUIDs in the platform; contracts and UI must show both index and UUID but **must** use UUIDs for any programmatic calls and manifest entries.
- Keep interactive prompts optional (controlled by `interactive` flag) to support automated execution.
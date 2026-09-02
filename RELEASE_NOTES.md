v0.2.0 — CLI & Notebook enhancements

Overview
- Adds a usable CLI surface to run common workflows locally and in CI.
- Expands notebook integration to make quickstarts and data downloads smoother.
- Updates examples and tests to demonstrate the new CLI + notebook flows.

Highlights
- CLI: `open_ksa/cli.py` — new entrypoints and runtime flags for downloads and manifest operations.
- Notebook: `open_ksa/notebook.py` — improved orchestration for interactive notebooks; examples updated in `examples/workbooks/`.
- Examples: new/updated scripts in `examples/scripts/` showing CLI usage.
- Tests: added/updated contract and integration tests covering CLI and notebook behaviors.

Migration notes
- If you previously used the library programmatically, minimal API adjustments may be required — consult `README.md` examples.
- For automated CI runs, ensure the CLI entrypoint is available in your packaging (set console_scripts / install extras if needed).

Acknowledgements & contributors
- Thanks to contributors who added tests, examples, and documentation to support this release.
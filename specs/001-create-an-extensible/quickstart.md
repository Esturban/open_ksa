# Quickstart: Install, run tests, and try the notebook

This quickstart explains how to set up a local development environment, run the test suite, and exercise the library using the provided example notebook `examples/workbooks/1_download_data.ipynb`.

Assumptions:
- You have Python 3.9+ installed and `venv` available.
- You are on macOS/Linux (commands may vary on Windows).

Steps:

1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install the package in editable mode and developer dependencies

```bash
pip install -e .[dev]
# If your pip doesn't support extras, run: pip install -e . && pip install -r requirements.txt
```

3. Run the test suite (fast unit/contract/integration tests)

```bash
pytest -q
```

4. Run a simple local script to exercise the organizations API (example)

Create `examples/scripts/0_quick_local_test.py` with:

```python
from open_ksa import organizations

# Lightweight smoke test
orgs = organizations()
print('Found', len(orgs.get('content', [])), 'organizations (sample)')
```

Run it:

```bash
python examples/scripts/0_quick_local_test.py
```

5. Notebook testing

- Open `examples/workbooks/1_download_data.ipynb` in Jupyter (`jupyter notebook` or `jupyter lab`).
- The workbook demonstrates the typical discovery → list → download flow. Cells that perform network access are annotated; when iterating rapidly during local development you can either:
  - Use smaller `size`/`limit` parameters to reduce the result set.
  - Mock network calls in tests using the provided `open_ksa/tests` fixtures.

6. Running tests that hit the network

Network tests are documented and marked in `pytest` when relevant. To run all tests including the slow/network ones, set an environment variable:

```bash
export CI_RUN_NETWORK=1
pytest -q
```

7. Development workflow recommendations

- Follow TDD: write a failing test under `open_ksa/tests/` before implementing new behavior.
- Use `black` and `ruff` for formatting and linting. Run:

```bash
ruff check . && black .
```

- When iterating on the example notebook, avoid re-downloading large datasets by using the `opendata/` cache folder created by the library.




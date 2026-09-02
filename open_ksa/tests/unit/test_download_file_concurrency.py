# REUSE_CHECKED: none -- searched open_ksa/tests for missing.json/missing_ids/concurrency
# coverage, nothing exists yet.
import importlib
import json
import threading
import time
from unittest.mock import MagicMock, patch

import requests

from open_ksa.download_file import download_file

# The open_ksa package re-exports `download_file` (the function) as an
# attribute named `download_file` on itself, which shadows the submodule of
# the same name -- `import open_ksa.download_file` would bind to the
# function, not the module. Go through sys.modules via importlib instead.
download_file_module = importlib.import_module("open_ksa.download_file")


def test_download_file_concurrent_writers_do_not_lose_missing_ids(tmp_path):
    """Several threads marking distinct resource_ids missing against the same
    missing.json must not lose updates or leave the file corrupted, even when
    a read and a write from different threads interleave."""
    missing_file_path = tmp_path / "missing.json"
    missing_file_path.write_text(json.dumps([]))

    resource_ids = [f"res-{i}" for i in range(8)]

    session = MagicMock()
    session.get.side_effect = requests.exceptions.RequestException("boom")

    original_load = json.load

    def slow_load(fp):
        data = original_load(fp)
        # Force a window between the read and the eventual write so
        # concurrent threads interleave deterministically.
        time.sleep(0.05)
        return data

    threads = []
    with patch.object(download_file_module.json, "load", side_effect=slow_load):
        for resource_id in resource_ids:
            thread = threading.Thread(
                target=download_file,
                kwargs=dict(
                    session=session,
                    url="https://example.com/data.csv",
                    headers={},
                    file_path=str(tmp_path / f"{resource_id}.csv"),
                    resource_id=resource_id,
                ),
            )
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    with open(missing_file_path) as f:
        final_missing_ids = json.load(f)

    assert set(final_missing_ids) == set(resource_ids)

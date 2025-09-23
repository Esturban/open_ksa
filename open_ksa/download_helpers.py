import os
import tempfile
import shutil
import csv
from typing import Iterator, List, Any


def atomic_write_bytes(target_path: str, chunk_iterator: Iterator[bytes]) -> int:
    """Write bytes from chunk_iterator to a temp file and atomically replace target_path.

    Returns total bytes written.
    """
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(target_path))
    total = 0
    with os.fdopen(fd, "wb") as fh:
        for chunk in chunk_iterator:
            fh.write(chunk)
            total += len(chunk)
        fh.flush()
        os.fsync(fh.fileno())
    # atomic replace
    shutil.move(tmp_path, target_path)
    return total


def save_stream_to_file(
    session, url: str, headers: dict, target_path: str, chunk_size: int = 8192
) -> int:
    """Stream a remote resource to disk atomically; returns total bytes written."""
    resp = session.get(url, headers=headers, stream=True)
    resp.raise_for_status()

    def chunks():
        for chunk in resp.iter_content(chunk_size):
            if chunk:
                yield chunk

    return atomic_write_bytes(target_path, chunks())


def stream_csv_sample(session, url: str, headers: dict, nrows: int) -> List[List[Any]]:
    """Stream CSV lines from URL and return up to nrows (not including header).

    Returns list of rows (including header as first row).
    """
    resp = session.get(url, headers=headers, stream=True)
    resp.raise_for_status()
    rows: List[List[Any]] = []
    reader = None
    count = 0
    for raw in resp.iter_lines(decode_unicode=True):
        if raw is None:
            continue
        line = raw
        if reader is None:
            # build initial reader with header
            reader = csv.reader([line])
            header = next(reader)
            rows.append(header)
            continue
        # parse regular row
        row_reader = csv.reader([line])
        row = next(row_reader)
        rows.append(row)
        count += 1
        if count >= nrows:
            break
    return rows

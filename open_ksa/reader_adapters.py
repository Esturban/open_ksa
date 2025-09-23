"""Reader adapters for supported formats.

Provide minimal adapter stubs: CSVAdapter, JSONAdapter, ExcelAdapter.
These will be extended in later tasks.
"""

from typing import Any, List
import csv
import json


class CSVAdapter:
    @staticmethod
    def read_stream(stream, nrows: int = None) -> List[dict]:
        reader = csv.DictReader(stream)
        rows: List[dict] = []
        for i, row in enumerate(reader):
            rows.append(row)
            if nrows is not None and i + 1 >= nrows:
                break
        return rows


class JSONAdapter:
    @staticmethod
    def read_stream(stream, nrows: int = None) -> List[dict]:
        rows: List[dict] = []
        for i, line in enumerate(stream):
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
            if nrows is not None and i + 1 >= nrows:
                break
        return rows


class ExcelAdapter:
    @staticmethod
    def read_file(path: str, nrows: int = None):
        raise NotImplementedError("ExcelAdapter.read_file is not implemented yet")

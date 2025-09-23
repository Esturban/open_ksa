import pytest


def test_reader_adapter_interface_exists():
    import importlib

    adapters = importlib.import_module("open_ksa.reader_adapters")
    # Expect adapter classes or factory functions to exist
    assert any(
        hasattr(adapters, name)
        for name in ("CSVAdapter", "JSONAdapter", "ExcelAdapter")
    ), "Reader adapter classes missing"

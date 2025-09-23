import io

try:
    from open_ksa.reader_adapters import CSVAdapter, JSONAdapter
except Exception:
    import sys
    import pathlib

    repo_root = pathlib.Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo_root))
    from open_ksa.reader_adapters import CSVAdapter, JSONAdapter


def test_csv_adapter_reads_nrows():
    csv_text = """id,name,age
1,Alice,30
2,Bob,25
3,Charlie,40
"""
    stream = io.StringIO(csv_text)
    rows = CSVAdapter.read_stream(stream, nrows=2)
    assert isinstance(rows, list)
    assert len(rows) == 2
    assert rows[0]["id"] == "1"
    assert rows[1]["name"] == "Bob"


def test_json_adapter_reads_nrows():
    json_lines = (
        '{"id":1,"name":"Alice"}\n{"id":2,"name":"Bob"}\n{"id":3,"name":"Charlie"}\n'
    )
    stream = io.StringIO(json_lines)
    rows = JSONAdapter.read_stream(stream, nrows=2)
    assert isinstance(rows, list)
    assert len(rows) == 2
    assert rows[0]["id"] == 1
    assert rows[1]["name"] == "Bob"

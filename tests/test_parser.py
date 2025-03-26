import os, json
from src.parser.extract import extract_tables

def test_extract_tables(tmp_path):
    output = tmp_path / "out.json"
    extract_tables("sample_data/sample_lab_report.pdf", str(output))
    data = json.loads(output.read_text())
    assert isinstance(data, list)

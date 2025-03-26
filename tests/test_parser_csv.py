import json
from src.parser.extract import extract_csv

def test_extract_csv(tmp_path):
    input_csv = "sample_data/patient_records.csv"
    output_json = tmp_path / "csv_output.json"
    extract_csv(input_csv, str(output_json))
    data = json.loads(output_json.read_text())
    assert isinstance(data, list)
    assert len(data) > 0
    # Check key presence
    assert "patient_id" in data[0]
    assert "name" in data[0]

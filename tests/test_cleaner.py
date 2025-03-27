import json
from src.cleaner.cleaner import clean_data

def test_clean_data(tmp_path):
    # Use parser output as input
    input_json = "parsed_data/report.json"
    output_json = tmp_path / "cleaned.json"
    clean_data(input_json, str(output_json))
    data = json.loads(output_json.read_text())
    assert isinstance(data, list)
    assert len(data) > 0

import json
from src.cleaner.cleaner import clean_data

def test_schema_validation(tmp_path):
    out = tmp_path / "clean.json"
    clean_data("sample_data/patient_records.csv", str(out))
    data = json.loads(out.read_text())
    assert all("patient_id" in rec for rec in data)

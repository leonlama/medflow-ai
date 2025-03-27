import json
from src.cleaner.cleaner import benchmark_clean

def test_benchmark(tmp_path):
    out = tmp_path / "bench.json"
    benchmark_clean("parsed_data/report.json", str(out))
    bench = json.loads(out.read_text())
    assert "cpu_time_seconds" in bench and bench["cpu_time_seconds"] > 0

import json, time
import pandas as pd
import pandera as pa

# CSV schema
schema_csv = pa.DataFrameSchema({
    "patient_id": pa.Column(str),
    "name": pa.Column(str), 
    "dob": pa.Column(pa.DateTime),
    "test_date": pa.Column(pa.DateTime),
    "test_type": pa.Column(str),
    "result": pa.Column(float),
    "units": pa.Column(str),
    "reference_range": pa.Column(str)
}, coerce=True)

def clean_data(input_path: str, output_path: str):
    df = pd.read_json(input_path)
    if "patient_id" in df.columns:
        df = schema_csv.validate(df)
    df = df.astype(str).drop_duplicates().ffill()
    df.to_json(output_path, orient="records", date_format="iso")

def benchmark_clean(input_path: str, output_path: str):
    start = time.perf_counter()
    clean_data(input_path, output_path)
    elapsed = time.perf_counter() - start
    with open("src/cleaner/benchmark.json", "w") as f:
        json.dump({"cpu_time_seconds": elapsed}, f)

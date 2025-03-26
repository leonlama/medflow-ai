import json
import pandas as pd

def clean_data(input_path: str, output_path: str):
    df = pd.read_json(input_path)
    # Safely drop duplicates by stringifying rows
    df = df.astype(str).drop_duplicates()
    df = df.ffill()
    df.to_json(output_path, orient="records", date_format="iso")

import pandas as pd
import os

path = os.path.join(os.path.dirname(__file__), "data", "processed", "SO_Order_Ageing.parquet")

try:
    df = pd.read_parquet(path)
    print("--- COLUMNS ---")
    for c in sorted(df.columns):
        print(f"- {c}")
except Exception as e:
    print(f"Error: {e}")

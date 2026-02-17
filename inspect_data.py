import pandas as pd
import sys

output_path = r"d:\User profile\67278\Desktop\SO Order\data_info.txt"
try:
    path = r"d:\User profile\67278\Desktop\SO Order\data\processed\SO_Order_Ageing.parquet"
    df = pd.read_parquet(path)
    with open(output_path, "w") as f:
        f.write("Columns:\n")
        f.write(str(df.columns.tolist()) + "\n")
        f.write("\nSample Data:\n")
        f.write(str(df.head(2).to_dict()) + "\n")
    print(f"Success! Output written to {output_path}")
except Exception as e:
    with open(output_path, "w") as f:
        f.write(f"Error: {e}")
    sys.exit(1)

import pandas as pd
import sys
import os

def convert_excel_to_parquet(input_file, output_file):
    """
    Converts an Excel file to Parquet format.
    """
    try:
        # Determine engine based on file extension
        file_ext = os.path.splitext(input_file)[1].lower()
        engine = 'openpyxl'
        if file_ext == '.xlsb':
            engine = 'pyxlsb'
            
        print(f"Reading Excel file: {input_file} (Engine: {engine})...")
        print("Reading sheet 'Raw Data' with header at row 1...")
        
        # Read Excel file
        # Using specific sheet 'Raw Data' and header=1 (skipping first empty row)
        df = pd.read_excel(input_file, engine=engine, sheet_name='Raw Data', header=1)
        
        print(f"Data shape: {df.shape}")
        
        # Convert object columns to string to ensure PyArrow compatibility
        # Ensure missing values are empty strings, not the string 'nan'
        for col in df.columns:
            if df[col].dtype == 'object' or df[col].dtype.name == 'category':
                df[col] = df[col].fillna("").astype(str).replace("nan", "")
                
        print(f"Writing Parquet file: {output_file}...")
        # Save as Parquet
        df.to_parquet(output_file, index=False)
        print(f"Successfully converted '{input_file}' to '{output_file}'")
    except Exception as e:
        print(f"Error converting file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python excel_to_parquet.py <input_excel_file> <output_parquet_file>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)
        
    convert_excel_to_parquet(input_path, output_path)

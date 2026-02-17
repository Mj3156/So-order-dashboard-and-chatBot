import pandas as pd
import os
import sys

def transform_summary():
    """
    Transform raw data into summary aggregations by Store Status.
    """
    input_path = "data/processed/SO_Order_Ageing.parquet"
    output_path = "data/transformed/summary.parquet"
    
    print(f"Reading data from {input_path}...")
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        sys.exit(1)
    
    try:
        # Read the processed data
        df = pd.read_parquet(input_path)
        
        print(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Define grouping column and metrics
        group_col = 'Store Status'
        numeric_cols = ['Open Qty Pcs', 'Allocated Qty Pcs', 'Picked Qty Pcs', 'Unallocated Qty Pcs']
        
        # Ensure numeric columns are numeric
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        print(f"Aggregating by {group_col}...")
        
        # Group and aggregate
        summary = df.groupby(group_col)[numeric_cols].sum().reset_index()
        
        # Calculate Grand Total
        total_row = pd.DataFrame(summary[numeric_cols].sum()).T
        total_row[group_col] = 'Grand Total'
        
        # Combine
        final_summary = pd.concat([summary, total_row], ignore_index=True)
        
        print(f"Summary computed: {len(final_summary)} rows")
        print(final_summary)
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save summary
        final_summary.to_parquet(output_path, index=False)
        print(f"\nSummary saved to {output_path}")
        
    except Exception as e:
        print(f"Error during transformation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    transform_summary()

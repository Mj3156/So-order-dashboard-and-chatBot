import pandas as pd
import os
import sys

def partition_by_status():
    """
    Partition data by Store Status for fast lookups.
    Manually creates partition folders to avoid categorical column issues.
    """
    input_path = "data/processed/SO_Order_Ageing.parquet"
    output_dir = "data/transformed/partitioned"
    
    print(f"Reading data from {input_path}...")
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
        sys.exit(1)
    
    try:
        # Read the processed data
        df = pd.read_parquet(input_path)
        
        print(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Get unique statuses
        partition_col = 'Store Status'
        if partition_col not in df.columns:
            print(f"Error: Column '{partition_col}' not found")
            sys.exit(1)
        
        statuses = df[partition_col].unique()
        print(f"Found {len(statuses)} unique statuses: {list(statuses)}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Manually partition - write each status to its own folder
        print(f"\nPartitioning data to {output_dir}...")
        
        for status in statuses:
            # Filter data for this status
            status_df = df[df[partition_col] == status].copy()
            
            # Create partition folder
            # Use URL encoding for special characters in folder names
            safe_status = status.replace(' ', '%20').replace('/', '%2F')
            partition_folder = os.path.join(output_dir, f"Store Status={safe_status}")
            os.makedirs(partition_folder, exist_ok=True)
            
            # Write to parquet WITHOUT the partition column (it's in the folder name)
            # This avoids categorical column issues
            status_df_no_partition = status_df.drop(columns=[partition_col])
            output_file = os.path.join(partition_folder, "data.parquet")
            status_df_no_partition.to_parquet(output_file, engine='pyarrow', index=False)
            
            print(f"  [OK] {status}: {len(status_df)} rows -> {partition_folder}")
        
        print(f"\nData partitioned successfully!")
        print(f"Partitions created in: {output_dir}")
        
    except Exception as e:
        print(f"Error during partitioning: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    partition_by_status()

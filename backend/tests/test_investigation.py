import sys
import os
import json
import pandas as pd

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.agent import run_pandas_query
from ai_engine.executor import load_dataset

def investigate():
    print("=== STARTING DATA INVESTIGATION ===\n")
    df = load_dataset("processed")
    
    # 1. Greater than 10 test
    print("--- 1. Ageing > 10 ---")
    q1 = "How many orders have Ageing greater than 10?"
    r1 = run_pandas_query(q1)
    
    # Manual check
    # Note: Column name is 'Ageing '
    manual_gt10 = len(df[df['Ageing '] > 10])
    manual_ge10 = len(df[df['Ageing '] >= 10])
    print(f"Agent Response: {r1}")
    print(f"Manual > 10: {manual_gt10}")
    print(f"Manual >= 10: {manual_ge10}")
    
    # 2. Men and Women Unallocated Qty
    print("\n--- 2. Division Men and Women ---")
    q2 = "Total Unallocated Qty for Division Men and Women."
    r2 = run_pandas_query(q2)
    
    # Manual check
    # Check if 'Men' and 'Women' are exactly like that in 'Division'
    unique_divisions = df['Division'].unique()
    print(f"Unique Divisions: {unique_divisions}")
    
    # Attempting manual calc with exact names
    mask = df['Division'].str.lower().isin(['men', 'women'])
    manual_sum = df[mask]['Unallocated Qty'].sum()
    print(f"Agent Response: {r2}")
    print(f"Manual Sum (Men/Women case-insensitive): {manual_sum}")

    # 3. Top 5 Regions by count
    print("\n--- 3. Top 5 Regions by count ---")
    q3 = "Top 5 Regions by count of orders."
    r3 = run_pandas_query(q3)
    manual_top5 = df['Region'].value_counts().head(5)
    print(f"Agent Response:\n{r3}")
    print(f"Manual Top 5:\n{manual_top5}")

if __name__ == "__main__":
    # Clear log first
    if os.path.exists("agent_debug.log"):
        os.remove("agent_debug.log")
    investigate()

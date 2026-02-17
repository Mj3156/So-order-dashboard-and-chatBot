import sys
import os
import pandas as pd
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.agent import run_pandas_query
from ai_engine.executor import execute_query_plan, load_dataset

def debug_summarizer_input():
    queries = [
        "Total Unallocated Qty for Region DELHI NCR?",
        "How many orders are in the dataset?"
    ]
    
    for q in queries:
        print(f"\n--- QUERY: {q} ---")
        # We'll simulate the plan generation and execution part to see the raw data
        # Step 1: Manual Plan (we know what the agent generates from the log)
        if "DELHI NCR" in q:
            plan = {"dataset": "processed", "operation": "sum", "metric": "Unallocated Qty", "filters": {"Region": {"op": "=", "value": "DELHI NCR"}}}
        else:
            plan = {"dataset": "processed", "operation": "count", "filters": {}}
            
        # Step 2: Execute
        result_df = execute_query_plan(plan)
        
        # Step 3: Format as in agent.py
        for col in result_df.select_dtypes(include=['number']).columns:
            result_df[col] = result_df[col].apply(lambda x: f"{x:,.0f}" if x == int(x) else f"{x:,.2f}")

        if len(result_df) > 1 or len(result_df.columns) > 1:
            data_str = result_df.to_markdown(index=False)
        else:
            data_str = result_df.to_string(index=False)
            
        print(f"RAW DATA STR FOR SUMMARY:\n'{data_str}'")
        
        # Now run the actual agent call to see the LLM summary
        print(f"AGENT RESPONSE:")
        print(run_pandas_query(q))

if __name__ == "__main__":
    debug_summarizer_input()

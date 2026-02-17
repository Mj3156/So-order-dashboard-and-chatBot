import sys
import os
import json
import pandas as pd

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.agent import run_pandas_query

def verify_multiturn():
    history = []
    
    # Step 1
    q1 = "Total Unallocated Qty for Region DELHI NCR?"
    print(f"--- Q1: {q1} ---")
    r1 = run_pandas_query(q1, history)
    print(f"Result 1:\n{r1}")
    history.append({"role": "user", "content": q1})
    history.append({"role": "assistant", "content": r1})
    
    # Step 2
    q2 = "Now show me that broken down by Department."
    print(f"\n--- Q2: {q2} ---")
    r2 = run_pandas_query(q2, history)
    print(f"Result 2:\n{r2}")
    history.append({"role": "user", "content": q2})
    history.append({"role": "assistant", "content": r2})
    
    # Step 3
    q3 = "Which of those has the highest Ageing?"
    print(f"\n--- Q3: {q3} ---")
    r3 = run_pandas_query(q3, history)
    print(f"Result 3:\n{r3}")

if __name__ == "__main__":
    if os.path.exists("agent_debug.log"):
        os.remove("agent_debug.log")
    verify_multiturn()

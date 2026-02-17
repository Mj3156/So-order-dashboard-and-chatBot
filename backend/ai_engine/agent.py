import json
from typing import List, Dict, Any
import pandas as pd

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Relative imports within the ai_engine package
from .schema import validate_query_plan
from .column_resolver import resolve_column_or_clarify
from .executor import execute_query_plan, load_dataset

MODEL = "llama3.2"

SYSTEM_PROMPT = """
You are a DATA QUERY PLANNER for a Sales Order dataset.

Your job is to convert the user's natural language query into a strict JSON query plan.

DATASET SCHEMA:
Columns: ['Priority', 'Sitealias', 'Sitecode', 'Region', 'State', 'Store Remark', 'Store Status', 'Zone', 'Division', 'Div Group', 'Section', 'Department', 'Article Code', 'Article Name', 'Seasonal Flag', 'Orderkey', 'Orderdate', 'Set Barcode', 'Sku Type', 'Sku Remark', 'Bom Qty', 'Openqty', 'Qtyallocated', 'Qtypicked', 'Unallocated Qty', 'Open Qty Pcs', 'Allocated Qty Pcs', 'Picked Qty Pcs', 'SO Balance', 'Unallocated Qty Pcs', 'Floor Pending Qty (Pcs)', 'Month', 'Ageing ', 'Ageing_Group', 'Type', 'Whseid', 'Warehouse']

CRITICAL: Note that the column 'Ageing ' has a trailing space.

COMMON VALUES:
- Store Status: ['Active', 'Hold', 'Closed']
- Seasonal Flag: ['SUMMER', 'WINTER', 'BASIC', 'CORE']
- Region: ['JHK1', 'WB1', ...]

RULES (STRICT):
1. Output MUST be valid JSON.
2. The JSON MUST include "operation", "dataset", and "metric" (if applicable).
3. "operation" MUST be one of: ["sum", "count", "group_sum", "group_count", "top_n", "bottom_n", "chat"].
4. "dataset" MUST be "processed" (default) or "transformed".
5. For "filters", use: {"Column Name": {"op": "=", "value": "value"}}.
6. Operator Precision (CRITICAL):
   - "Greater than" or "More than" ALWAYS uses ">".
   - "At least" or "Greater than or equal to" ALWAYS uses ">=".
   - "Less than" or "Fewer than" ALWAYS uses "<".
   - "At most" uses "<=".
7. For multiple values (e.g. "Men and Women"), use "op": "in" and "value": ["Val1", "Val2"].
8. For "count", use "operation": "count". For "count of [Entity]", use "operation": "group_count".
9. For "top_n" of an entity (e.g. "Top 5 Regions"), "group_by" should be the entity (["Region"]).
   - OMIT "metric" for "Top N by count". Include "metric" for summing.
   - NEVER add a filter on the group_by column (e.g. {"Region": "=": "..."}) unless specifically asked.
10. NEVER add a filter with "value": null. If no filter is needed, omit the "filters" key.

CRITICAL:
- ONLY output the JSON plan.
- NEVER provide sample data, mock numbers, or "Here is the result" text.
- If you see a previous result in the history like "[RESULT] ...", treat it as the output of your previous query. DO NOT imitate its format.
- DO NOT say "I'm not sure what operation to perform" if the user's question follows a previous query about a metric.
- PERSISTENCE: Filters from previous turns MUST be carried over to current turns unless they are contradictory.
- REFERENCES: When a user says "those", "them", or "that breakdown", refer to the "group_by" column of the previous response in the history.
- IMPORTANT: If the user asks for "Total" or "Sum" of a metric for certain groups, use "operation": "sum" with a filter. ONLY use "group_sum" if they use the words "breakdown", "by", or "per".
- Partial Matching: If a user filters for "Women", the executor will automatically find "Women Western" and "Women Ethnic". You just need to provide the value "Women".

Example 2: "Total Unallocated Qty for Division Men and Women"
{
    "dataset": "processed",
    "operation": "sum",
    "metric": "Unallocated Qty",
    "filters": {"Division": {"op": "in", "value": ["Men", "Women"]}}
}

Example 3: "Sum of Unallocated Qty broken down by Division"
{
    "dataset": "processed",
    "operation": "group_sum",
    "group_by": ["Division"],
    "metric": "Unallocated Qty"
}

Example 4: "Top 5 Regions by count of orders"
{
    "dataset": "processed",
    "operation": "top_n",
    "group_by": ["Region"],
    "limit": 5
}

Example 5: "Orders with Ageing greater than 50"
{
    "dataset": "processed",
    "operation": "count",
    "filters": {"Ageing ": {"op": ">", "value": 50}}
}

CONVERSATION EXAMPLE:
User: "Total Unallocated Qty for Region DELHI NCR?"
Assistant: [RESULT] 15,000 [/RESULT]
User: "Now show me that broken down by Department."
{
    "dataset": "processed",
    "operation": "group_sum",
    "group_by": ["Department"],
    "metric": "Unallocated Qty",
    "filters": {"Region": {"op": "=", "value": "DELHI NCR"}}
}
Assistant: [RESULT] | Dept | Sum | ... [/RESULT]
User: "Which of those has the highest Ageing?"
{
    "dataset": "processed",
    "operation": "top_n",
    "group_by": ["Department"],
    "metric": "Ageing ",
    "filters": {"Region": {"op": "=", "value": "DELHI NCR"}},
    "limit": 1
}
"""

SUMMARY_PROMPT = """
You are a helpful DATA ANALYST. 
The user asked: "{query}"
The actual data result is: {result}

If the result is a single number or a very short list, convert it into a single, natural language sentence that answers the user's question directly (e.g., "9,661 orders have ageing greater than 50").
If the result is a large table, just provide a very brief introductory sentence like "Here are the top 5 regions by unallocated quantity:" followed by the original table.
STRICT: DO NOT use [RESULT] tags in your output.
"""

def run_pandas_query(query: str, history: List[Dict[str, str]] | None = None) -> str:
    """
    Main entry point for the AI Agent.
    Orchestrates: LLM -> Plan -> Resolve Columns -> Validate -> Execute.
    """
    llm = ChatOllama(model=MODEL, temperature=0)

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    
    # Add history if provided
    if history:
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                # Provide the previous assistant response as an AIMessage
                # We mention it's a data result to help the LLM understand it's the output of its previous plan
                content = msg["content"]
                messages.append(AIMessage(content=f"Data Result: {content}"))

    messages.append(HumanMessage(content=query))

        # ---------------- STEP 1: PLAN ----------------
    try:
        response = llm.invoke(messages)
        plan_raw = response.content if response else ""

        if not plan_raw.strip():
            return "I couldn't generate a plan for that query. Please try rephrasing."

        # Robust JSON Extraction
        def extract_first_json(text):
            text = text.strip()
            # Remove comments (simple regex-like removal of //)
            import re
            text = re.sub(r'//.*?\n', '\n', text)
            
            # Handle markdown blocks
            if "```json" in text:
                 text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                 text = text.split("```")[1].split("```")[0]
            
            start = text.find("{")
            if start == -1: return None
            
            # Extract balance brackets
            count = 0
            for i in range(start, len(text)):
                char = text[i]
                if char == "{": count += 1
                elif char == "}":
                    count -= 1
                    if count == 0:
                        content = text[start:i+1]
                        # Final safety: remove trailing commas before }
                        content = re.sub(r',\s*}', '}', content)
                        return content
            return None

        plan_json = extract_first_json(plan_raw)
        if not plan_json:
             # If no JSON found, treat the whole response as a 'chat' reply if it looks like text
             if len(plan_raw.strip()) > 0 and "{" not in plan_raw:
                 return plan_raw.strip()
             return f"I received an invalid response from the AI. Raw response: {plan_raw[:100]}"

        plan = json.loads(plan_json)
        
        # ---------------- HANDLE 'CHAT' EARLY ----------------
        if plan.get("operation") == "chat":
            return plan.get("message", "I am a data agent.")

        # Ensure operation exists
        if not plan.get("operation") or plan.get("operation") == "None":
             # Try to infer operation if missing in follow-up
             if "group_by" in plan and plan["group_by"]:
                 plan["operation"] = "top_n" if "limit" in plan or "n" in plan else "group_sum"
             elif "metric" in plan:
                 plan["operation"] = "sum"
             else:
                 plan["operation"] = "chat"
                 plan["message"] = "I'm not sure what operation to perform. Could you clarify?"

        # Default dataset if not provided
        if "dataset" not in plan:
            plan["dataset"] = "processed"
            
        allowed_datasets = ["processed", "transformed"]
        if plan["dataset"] not in allowed_datasets:
             plan["dataset"] = "processed"

        # ---------------- DOUBLE CHECK 'CHAT' AFTER AUTO-CORRECT ----------------
        if plan.get("operation") == "chat":
            return plan.get("message", "I am a data agent.")
 
    except Exception as e:
        return f"I couldn't understand your question. Error: {str(e)}"

    # ---------------- STEP 2: LOAD DATA ----------------
    # We load data here to get the list of available columns for resolution
    try:
        df = load_dataset(plan.get("dataset", "processed"))
        columns = df.columns.tolist()
    except Exception as e:
        return f"Error loading data: {str(e)}"

    # ---------------- STEP 3: COLUMN RESOLUTION ----------------
    def resolve_or_ask(field: str):
        # This function tries to resolve a user-friendly name to a strict column name.
        # If ambiguous, it returns the user question string.
        resolved, candidates = resolve_column_or_clarify(field, columns)
        
        if resolved:
            return resolved
        if candidates:
            # If ambiguous, asking the user to clarify IS the response.
            return f"Which column do you mean: {', '.join(candidates)}?"
        
        # If not resolved and not ambiguous (no match), return original for validation to catch.
        return field

    # Resolve 'metric'
    if plan.get("metric") is not None:
        result = resolve_or_ask(plan["metric"])
        if isinstance(result, str) and result.startswith("Which column"):
            return result
        plan["metric"] = result

    # Resolve 'group_by'
    if plan.get("group_by") is not None:
        gb = plan["group_by"]
        if isinstance(gb, str):
            result = resolve_or_ask(gb)
            if isinstance(result, str) and result.startswith("Which column"):
                return result
            plan["group_by"] = result
        elif isinstance(gb, list):
            new_gb = []
            for col in gb:
                if col is None: continue
                result = resolve_or_ask(col)
                if isinstance(result, str) and result.startswith("Which column"):
                    return result
                new_gb.append(result)
            plan["group_by"] = new_gb

    # AUTO-CORRECT: Move 'metric' to 'group_by' ONLY IF 'metric' is actually a categorical column 
    # and group_by is missing. This happens when LLM says {"op": "top_n", "metric": "Department"}
    if plan.get("operation") in ["group_count", "group_sum", "top_n", "bottom_n"]:
        if "group_by" not in plan or not plan["group_by"]:
             if "metric" in plan:
                 # Only move if it's not a known numeric metric
                 numeric_cols = ["Unallocated Qty", "Openqty", "Qtyallocated", "Qtypicked", "SO Balance", "Ageing "]
                 if plan["metric"] not in numeric_cols:
                     plan["group_by"] = [plan["metric"]]
                     if plan["operation"] in ["top_n", "bottom_n"]:
                         del plan["metric"]
    
    # AUTO-CORRECT: Remove 'metric' if operation is count/group_count or if metric is "count"
    # (Only do this AFTER potential migration above)
    if plan.get("operation") in ["count", "group_count", "top_n", "bottom_n"]:
        if "metric" in plan and str(plan["metric"]).lower() in ["count", "total"]:
            del plan["metric"]
    
    if plan.get("operation") in ["count", "group_count"]:
        if "metric" in plan:
            del plan["metric"]

    # Resolve 'filters'
    if "filters" in plan:
        new_filters = {}
        # Remove null values or empty filters
        if not isinstance(plan["filters"], dict):
             plan["filters"] = {}
             
        for col, cond in list(plan["filters"].items()):
            if not cond or not isinstance(cond, dict) or cond.get("value") is None:
                continue
                
            result = resolve_or_ask(col)
            if isinstance(result, str) and result.startswith("Which column"):
                return result
            new_filters[result] = cond
        plan["filters"] = new_filters

    # ---------------- STEP 4: VALIDATE ----------------
    try:
        validate_query_plan(plan, columns)
    except Exception as e:
        return f"Invalid query: {str(e)}"

    # AUTO-CORRECT: If operation is top_n/bottom_n and metric is a known ID column, remove it to force Count mode
    if plan.get("operation") in ["top_n", "bottom_n"]:
        if "metric" in plan and plan["metric"]:
            id_cols = ["Orderkey", "Orderno", "Article Number"]
            if plan["metric"] in id_cols:
                del plan["metric"]
    try:
        with open("agent_debug.log", "a") as f:
            f.write(f"\nQUERY: {query}\n")
            f.write(f"PLAN: {json.dumps(plan)}\n")
        result_df = execute_query_plan(plan)
    except Exception as e:
        with open("agent_debug.log", "a") as f:
            f.write(f"EXECUTION ERROR: {str(e)}\n")
        return f"Calculation Error: {str(e)}"

    # Format numeric columns with commas for readability
    for col in result_df.select_dtypes(include=['number']).columns:
        # Use comma separator for thousands
        result_df[col] = result_df[col].apply(lambda x: f"{x:,.0f}" if x == int(x) else f"{x:,.2f}")

    # Return as Markdown table for better UI rendering
    if len(result_df) > 1 or len(result_df.columns) > 1:
        data_str = result_df.to_markdown(index=False)
    else:
        # For single values, provide a very explicit format to avoid LLM confusion
        val = result_df.iloc[0, 0]
        col = result_df.columns[0]
        data_str = f"Result Value: {val} (Metric: {col})"
        
    # ---------------- STEP 6: SUMMARIZE (Natural Language) ----------------
    try:
        # Use a single, clear instruction for natural language summarization.
        # This prevents the LLM from returning raw data or empty strings.
        instruction = f"""
        Answer the following question using the provided Data Result.
        
        Question: "{query}"
        Data Result: {data_str}
        
        Your Goal: 
        Convert the Data Result into a single, direct natural language sentence that answers the Question. 
        
        Example 1 (Single Value):
        Question: "How many orders have ageing > 50?"
        Data Result: "Result Value: 9,661 (Metric: count)"
        Summary: "There are 9,661 orders with ageing greater than 50."
        
        Example 2 (Table):
        Question: "Top 3 regions?"
        Data Result: "| Region | ... |"
        Summary: "Here are the top 3 regions: [Table]"
        
        STRICT RULES:
        1. Accuracy is priority. If the value is 8,896, say 8,896.
        2. Do not hallucinate. Use ONLY the Data Result provided.
        3. If it's a table, keep the table exactly as it is after your intro sentence.
        """
        
        summary_msg = [HumanMessage(content=instruction)]
        summary_resp = llm.invoke(summary_msg)
        
        final_text = summary_resp.content.strip() if summary_resp else data_str
        
        # Cleanup potential LLM artifacts
        final_text = final_text.strip('"').strip("'")
        for prefix in ["Data Result:", "Answer:", "Result:", "Summary:"]:
            if final_text.startswith(prefix):
                final_text = final_text[len(prefix):].strip()
        
        if not final_text:
            return data_str
            
        return final_text
    except:
        return data_str

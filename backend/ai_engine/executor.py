import pandas as pd
import os

BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data")

def load_dataset(name: str):
    path = os.path.join(BASE_PATH, "processed", "SO_Order_Ageing.parquet")
    return pd.read_parquet(path)

def execute_query_plan(plan: dict):
    df = load_dataset(plan.get("dataset", "processed"))

    # apply filters
    filters = plan.get("filters", {})
    if filters:
        for col, condition in filters.items():
            op = condition.get("op")
            val = condition.get("value")
            
            # Helper for case-insensitive string comparison
            def get_mask(df, col, op, val):
                if isinstance(val, str) and op in ["=", "!=", "in", "not in"]:
                    col_str = df[col].astype(str)
                    if op in ["=", "eq"]: 
                        exact = col_str.str.lower() == val.lower()
                        if not exact.any():
                            # Fallback to partial match if no exact match found
                            return col_str.str.lower().str.contains(val.lower())
                        return exact
                    if op == "!=": return col_str.str.lower() != val.lower()
                    if op == "in": 
                        vals = [v.lower() for v in (val if isinstance(val, list) else [val])]
                        return col_str.str.lower().isin(vals)
                    if op == "not in":
                        vals = [v.lower() for v in (val if isinstance(val, list) else [val])]
                        return ~col_str.str.lower().isin(vals)
                
                # Standard comparisons (with numeric conversion safety)
                target_val = val
                is_num = pd.api.types.is_numeric_dtype(df[col])
                if not isinstance(val, (int, float, list)) and is_num:
                    try:
                        target_val = float(val) if "." in str(val) else int(val)
                    except:
                        pass
                
                if op in ["=", "eq"]: return df[col] == target_val
                if op == "!=": return df[col] != target_val
                if op == ">": return df[col] > target_val
                if op == "<": return df[col] < target_val
                if op == ">=": return df[col] >= target_val
                if op == "<=": return df[col] <= target_val
                if op == "in": return df[col].isin(val if isinstance(val, list) else [val])
                if op == "not in": return ~df[col].isin(val if isinstance(val, list) else [val])
                return None

            mask = get_mask(df, col, op, val)
            if mask is not None:
                df = df[mask]

    if plan["operation"] == "sum":
        return pd.DataFrame({
            plan["metric"]: [df[plan["metric"]].sum()]
        })
    elif plan["operation"] == "count":
        return pd.DataFrame({"count": [len(df)]})

    if plan["operation"] == "group_sum":
        res = df.groupby(plan["group_by"])[plan["metric"]].sum()
        if isinstance(res, pd.Series):
            return res.reset_index()
        return res.reset_index()
    elif plan["operation"] == "group_count":
        return (
            df.groupby(plan["group_by"])
            .size()
            .reset_index(name="count")
        )
    elif plan["operation"] in ["top_n", "bottom_n"]:
         # Robust implementation: Sum if metric provided, otherwise Count
        group_cols = plan["group_by"]
        
        if "metric" in plan and plan["metric"]:
            # Summation Mode
            metric_col = plan["metric"]
            agg = df.groupby(group_cols)[metric_col].sum().reset_index()
            sort_col = metric_col
        else:
            # Count Mode
            agg = df.groupby(group_cols).size().reset_index(name="count")
            sort_col = "count"

        ascending = (plan["operation"] == "bottom_n")
        limit = plan.get("limit", plan.get("n", 5))
        
        return agg.sort_values(sort_col, ascending=ascending).head(limit)

    raise ValueError(f"Unsupported operation: {plan['operation']}")

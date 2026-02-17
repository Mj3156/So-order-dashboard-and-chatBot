# backend/schema.py

from typing import Dict, List, Any


# ===============================
# DATASET REGISTRY
# ===============================

DATASETS = {
    "processed": {
        "path": "data/processed/SO_Order_Ageing.parquet",
        "description": "Raw processed SO order data (row-level)"
    },
    "transformed": {
        "path": "data/transformed/summary.parquet",
        "description": "Pre-aggregated trusted summary data"
    }
}


# ===============================
# ALLOWED OPERATIONS
# ===============================

ALLOWED_OPERATIONS = {
    "sum",
    "count",
    "group_sum",
    "group_count",
    "top_n",
    "top_n",
    "bottom_n",
    "chat"
}


# ===============================
# ALLOWED FILTER OPERATORS
# ===============================

ALLOWED_FILTER_OPERATORS = {
    "=",
    "eq",
    "!=",
    "in",
    "not in",
    ">",
    "<",
    ">=",
    "<="
}


# ===============================
# QUERY PLAN VALIDATION
# ===============================

def validate_query_plan(
    plan: Dict[str, Any],
    available_columns: List[str]
) -> None:
    """
    Validates an LLM-generated query plan.
    Raises ValueError if anything is invalid.
    """

    # ---------- Dataset ----------
    dataset = plan.get("dataset")
    if dataset not in DATASETS:
        raise ValueError(
            f"Invalid dataset '{dataset}'. "
            f"Allowed datasets: {list(DATASETS.keys())}"
        )

    # ---------- Operation ----------
    operation = plan.get("operation")
    if operation not in ALLOWED_OPERATIONS:
        raise ValueError(
            f"Invalid operation '{operation}'. "
            f"Allowed operations: {sorted(ALLOWED_OPERATIONS)}"
        )

    # ---------- Metric ----------
    metric = plan.get("metric")
    if metric:
        if metric not in available_columns:
            raise ValueError(
                f"Metric column '{metric}' not found. "
                f"Available columns: {available_columns}"
            )

    # ---------- Group By ----------
    group_by = plan.get("group_by", [])
    if group_by:
        if not isinstance(group_by, list):
            raise ValueError("group_by must be a list of column names")
        for col in group_by:
            if col not in available_columns:
                raise ValueError(
                    f"group_by column '{col}' not found. "
                    f"Available columns: {available_columns}"
                )

    # ---------- Filters ----------
    filters = plan.get("filters", {})
    if filters:
        if not isinstance(filters, dict):
            raise ValueError("filters must be a dictionary")

        for col, condition in filters.items():
            if col not in available_columns:
                raise ValueError(
                    f"Filter column '{col}' not found. "
                    f"Available columns: {available_columns}"
                )

            if not isinstance(condition, dict):
                raise ValueError(
                    f"Filter for '{col}' must be a dict with 'op' and 'value'"
                )

            op = condition.get("op")
            if op not in ALLOWED_FILTER_OPERATORS:
                raise ValueError(
                    f"Invalid filter operator '{op}' for column '{col}'. "
                    f"Allowed operators: {sorted(ALLOWED_FILTER_OPERATORS)}"
                )

    # ---------- Limit ----------
    limit = plan.get("limit")
    if limit is not None:
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        if limit > 100:
            raise ValueError("limit cannot exceed 100 rows")

    # ---------- Order ----------
    order = plan.get("order")
    if order:
        if order not in ("asc", "desc"):
            raise ValueError("order must be 'asc' or 'desc'")

    # If we reach here, the plan is valid
    return

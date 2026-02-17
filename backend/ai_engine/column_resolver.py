from typing import Tuple, List, Optional

def resolve_column_or_clarify(
    requested_column: str,
    available_columns: List[str]
) -> Tuple[Optional[str], Optional[List[str]]]:
    """
    Resolves a requested column name against available columns.
    
    Returns:
        (ResolvedName, None) if exactly one match found.
        (None, [Candidates]) if ambiguous.
        (None, None) if no match.
    
    STRICT AMBIGUITY CHECK:
    If 'requested_column' matches an exact column, BUT is also a prefix/substring
    of another column, we treat it as ambiguous to prevent accidental wrong selection.
    Example: 'Unallocated Qty' vs 'Unallocated Qty Pcs'.
    """
    if requested_column is None:
        return None, None
    requested_lower = requested_column.lower().strip()
    
    # 0. SYNONYMS & CLEANING
    def clean_and_normalize(s: str) -> str:
        s = s.lower().strip()
        # Common Synonyms
        s = s.replace("quantity", "qty")
        s = s.replace("number", "no")
        s = s.replace("code", "cd")
        s = s.replace("identifier", "id")
        # Remove separators
        s = s.replace("_", "").replace(" ", "")
        return s

    norm_req = clean_and_normalize(requested_lower)

    # 0.1 SPECIAL ALIASES
    ALIASES = {
        "allocatedqty": "Qtyallocated",
        "qtyallocated": "Qtyallocated",
        "pickedqty": "Qtypicked",
        "qtypicked": "Qtypicked",
        "openqty": "Openqty",
        "orderdate": "Orderdate",
        "orderkey": "Orderkey",
        "sitealias": "Sitealias",
        "sitecode": "Sitecode",
        "whseid": "Whseid",
        "warehouseid": "Whseid",
        "bomqty": "Bom Qty",
        "setbarcode": "Set Barcode",
        "skuremark": "Sku Remark",
        "skutype": "Sku Type",
        "storeremark": "Store Remark",
        "storestatus": "Store Status",
        "ageing": "Ageing " # Handle the trailing space!
    }

    # Direct Alias Check
    if norm_req in ALIASES:
        target = ALIASES[norm_req]
        if target in available_columns:
            return target, None

    # 1. Exact Match (Case Insensitive)
    exact_matches = [c for c in available_columns if c.lower().strip() == requested_lower]
    if len(exact_matches) == 1:
        return exact_matches[0], None

    # 2. Normalized Match (Eq)
    norm_candidates = [c for c in available_columns if clean_and_normalize(c) == norm_req]
    if len(norm_candidates) == 1:
        return norm_candidates[0], None
    if len(norm_candidates) > 1:
        return None, norm_candidates

    # 3. Partial Match (Substring of Original)
    # Check if the requested string is a substring of any column
    candidates = [c for c in available_columns if requested_lower in c.lower().strip()]
    
    # Special check for 'Ageing ' if not found yet
    if not candidates and "ageing" in requested_lower:
        candidates = [c for c in available_columns if "ageing" in c.lower()]

    # 4. Partial Match (Substring of Normalized) - Fallback
    if not candidates:
        candidates = [c for c in available_columns if norm_req in clean_and_normalize(c)]

    if len(candidates) == 1:
        return candidates[0], None
        
    if len(candidates) > 1:
        # Sort candidates to prefer shorter matches or exact prefix matches
        candidates.sort(key=len)
        return None, candidates

    return None, None

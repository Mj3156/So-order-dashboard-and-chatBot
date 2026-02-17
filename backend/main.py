from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
import pandas as pd

# Add project root to path so 'backend' module can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the clean agent
from backend.ai_engine.agent import run_pandas_query

print("\n*** SO ORDER BACKEND - REWRITTEN & VERIFIED ***\n")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants - paths relative to backend/ (where main.py is run from)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SUMMARY_PATH = os.path.join(DATA_DIR, "transformed", "summary.parquet")
PARTITIONED_DIR = os.path.join(DATA_DIR, "transformed", "partitioned")

# Ensure static directory exists
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ---------------------------
# MODELS
# ---------------------------

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    history: List[ChatMessage] = []

# ---------------------------
# ROUTES
# ---------------------------

@app.get("/")
def root():
    return {"status": "OK", "service": "SO Order Ageing API"}

@app.get("/summary")
async def get_summary():
    """
    Serve pre-computed summary data.
    """
    if not os.path.exists(SUMMARY_PATH):
        raise HTTPException(status_code=500, detail=f"Summary file not found at {SUMMARY_PATH}")
    
    try:
        df = pd.read_parquet(SUMMARY_PATH)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading summary: {str(e)}")

@app.get("/details/{status}")
async def get_details(status: str, page: int = 1, page_size: int = 1000, search: str = ""):
    """
    Serve data for a specific Store Status from partitioned data with pagination.
    """
    try:
        # Validate pagination parameters
        if page < 1:
            raise HTTPException(status_code=400, detail="Page must be >= 1")
        if page_size < 1 or page_size > 10000:
            raise HTTPException(status_code=400, detail="Page size must be between 1 and 10000")
        
        # Handle Grand Total - return paginated rows from all data
        if status == 'Grand Total':
            all_data_path = os.path.join(DATA_DIR, "processed", "SO_Order_Ageing.parquet")
            if not os.path.exists(all_data_path):
                raise HTTPException(status_code=404, detail="Data file not found")
            
            df = pd.read_parquet(all_data_path, engine='pyarrow')
        else:
             # Read from partitioned data - use URL encoding for folder name
            safe_status = status.replace(' ', '%20').replace('/', '%2F') 
            partition_folder = os.path.join(PARTITIONED_DIR, f"Store Status={safe_status}")
            partition_file = os.path.join(partition_folder, "data.parquet")
            
            if not os.path.exists(partition_file):
                raise HTTPException(status_code=404, detail=f"No data found for status: {status}")
            
            df = pd.read_parquet(partition_file, engine='pyarrow')

        # Apply fast vectorized search on text-like columns
        if search and search.strip() and not df.empty:
            search_lower = search.lower()
            mask = pd.Series(False, index=df.index)
            for col in df.columns:
                # Only search non-numeric columns for speed and stability
                if not pd.api.types.is_numeric_dtype(df[col]):
                    mask |= df[col].astype(str).str.contains(search_lower, case=False, na=False)
            df = df[mask]
            
        total_rows = len(df)
        
        # Calculate pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        if start_idx >= total_rows:
            return {
                "data": [],
                "total_rows": total_rows,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_rows + page_size - 1) // page_size,
                "returned_rows": 0,
                "status": status
            }
        
        df_page = df.iloc[start_idx:end_idx]
        
        # Convert to dict and ensure any 'nan' strings (if any) are empty
        results = df_page.fillna("").to_dict(orient="records")
        for row in results:
            for key, value in row.items():
                if value == "nan":
                    row[key] = ""
                    
        return {
            "data": results,
            "total_rows": total_rows,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_rows + page_size - 1) // page_size,
            "returned_rows": len(df_page),
            "status": status
        }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        # Convert pydantic models to dicts for history
        response = run_pandas_query(
            query=request.query,
            history=[m.model_dump() for m in request.history]
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # If run as script (python backend/main.py), this is executed.
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)

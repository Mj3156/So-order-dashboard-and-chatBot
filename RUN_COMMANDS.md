# SO Order Ageing System - Run Commands

## ⚠️ IMPORTANT: Always Run from Project Root
All commands below must be run from the project root directory:
```powershell
cd "D:\User profile\67278\Desktop\SO Order"
```

**DO NOT** run commands from inside `backend/`, `frontend/`, or `etl/` folders!

---

## Start Backend (Terminal 1)
```powershell
# Make sure you're in the project root first!
cd "D:\User profile\67278\Desktop\SO Order"

# Then start the backend
uvicorn backend.main:app --host 127.0.0.1 --port 8008 --reload
```

## Start Frontend (Terminal 2)
```powershell
# Make sure you're in the project root first!
cd "D:\User profile\67278\Desktop\SO Order"

# Then start the frontend
streamlit run frontend/app.py --server.port 8502
```

## Access the Application
- **Frontend Dashboard**: http://localhost:8502
- **Backend API**: http://localhost:8008
- **API Documentation**: http://localhost:8008/docs

## Stop the Servers
Press `Ctrl+C` in each terminal window.

## Re-run ETL (if data changes)
```powershell
# Make sure you're in the project root first!
cd "D:\User profile\67278\Desktop\SO Order"

# 1. Convert Excel to Parquet
python etl/excel_to_parquet.py "data/raw/SO Order Ageing 31st Jan 2026..xlsb" "data/processed/SO_Order_Ageing.parquet"

# 2. Generate summary
python etl/transform_summary.py

# 3. Partition data
python etl/partition_by_status.py
```

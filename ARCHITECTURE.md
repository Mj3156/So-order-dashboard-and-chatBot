
# System Architecture

## Overview
The **SO Order Ageing System** is a data analytics platform designed to process, analyze, and visualize sales order ageing data. It features a modern web interface, a FastAPI backend with AI capabilities, and an ETL pipeline for data processing.

## Components

### 1. Data Pipeline (ETL)
**Directory**: `etl/`
- **Purpose**: Ingests raw Excel data, transforms it, and optimizes it for query performance.
- **Key Scripts**:
    - `excel_to_parquet.py`: Converts raw `.xlsb` files to Parquet format for high-performance reading.
    - `transform_summary.py`: Aggregates data and produces summary statistics.
    - `partition_by_status.py`: Partitions the main dataset by "Store Status" to optimize frontend query performance.
- **Output**: 
    - `data/processed/`: Raw Parquet conversions.
    - `data/transformed/`: Aggregated and partitioned Parquet files.

### 2. Backend API
**Directory**: `backend/`
- **Tech Stack**: Python, FastAPI, Pandas, LangChain, Ollama.
- **Port**: 8008
- **Responsibilities**:
    - Serves pre-computed summary data (`/summary`).
    - serves paginated detailed data with fast filtering (`/details/{status}`).
    - **AI Architecture** (`backend/ai_engine/`):
        - **Agent**: Parses natural language into query plans (`agent.py`).
        - **Executor**: Runs optimized pandas queries (`executor.py`).
        - **Resolver**: Handles column name ambiguity (`column_resolver.py`).

### 3. Frontend Application
**Directory**: `frontend-nextjs/`
- **Tech Stack**: Next.js, React, Tailwind CSS, TypeScript.
- **Port**: 3000 (standard Next.js dev port) or configurable.
- **Features**:
    - Interactive Dashboard showing key metrics.
    - Chat Assistant for AI-driven data analysis using charts and insights.
    - Detailed data grids with filtering and pagination.

## Data Flow
1. **Ingestion**: Raw Excel file -> ETL Scripts -> Parquet Files.
2. **Serving**: Backend reads Parquet files directly (no database required for this read-heavy workload).
3. **AI Analysis**: User Question -> API -> LangChain Agent -> Pandas DataFrame Analysis -> Response.

## Integration Points
- **Frontend -> Backend**: REST API calls to `http://localhost:8008`.
- **Backend -> Data**: Direct file system access to `data/` directory.
- **Backend -> Ollama**: Local HTTP requests to `http://localhost:11434`.

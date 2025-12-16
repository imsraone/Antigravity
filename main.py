import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import pandas as pd
from datetime import datetime

# Local imports
import database
import llm_service

app = FastAPI(title="Text-to-SQL AI Agent")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize DB on startup
@app.on_event("startup")
def startup_event():
    database.init_db()

# Request model
class QueryRequest(BaseModel):
    prompt: str

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.post("/generate-and-run")
async def generate_and_run(request: QueryRequest):
    try:
        # 1. Get Schema
        schema = database.get_schema()
        
        # 2. Generate SQL (Mock LLM)
        sql_query = llm_service.generate_sql_from_prompt(schema, request.prompt)
        
        # 3. Execute SQL
        df = database.execute_query(sql_query)
        
        # 4. Save to Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"query_results_{timestamp}.xlsx"
        file_path = f"static/downloads/{filename}"
        
        # Ensure download directory exists
        os.makedirs("static/downloads", exist_ok=True)
        
        df.to_excel(file_path, index=False)
        
        # Convert df to dict for frontend display preview
        preview_data = df.head(10).to_dict(orient="records")
        columns = df.columns.tolist()

        return {
            "sql_query": sql_query,
            "excel_url": f"/static/downloads/{filename}",
            "preview": preview_data,
            "columns": columns,
            "row_count": len(df)
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

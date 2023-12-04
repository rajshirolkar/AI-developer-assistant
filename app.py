from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class QueryInput(BaseModel):
    sql_query: str

@app.post("/query-plan")
def get_query_plan(query_input: QueryInput):
    # Connect to the SQLite database
    try:
        conn = sqlite3.connect('chinook.db')
        cursor = conn.cursor()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Get the query plan
    try:
        plan_query = f"EXPLAIN QUERY PLAN {query_input.sql_query}"
        cursor.execute(plan_query)
        plan = cursor.fetchall()
        # Adding column names to the response
        columns = ["id", "parent", "notused", "detail"]
        plan_with_columns = [dict(zip(columns, row)) for row in plan]
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    
    cursor.close()
    conn.close()

    return {"query_plan": plan_with_columns}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

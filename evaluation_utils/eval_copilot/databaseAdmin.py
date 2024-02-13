from fastapi import FastAPI, Depends
from fastapi_admin.app import app as admin_app
from fastapi_admin.factory import app as admin_factory
from fastapi_admin.providers.login import UsernamePasswordProvider
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
import pandas as pd
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Read data from CSV
df = pd.read_csv("data.csv")

# Define SQLAlchemy model (assuming CSV has columns: id, name, value)
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    value = Column(String)

# Setup Async Engine for fastapi-admin
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, echo=True)

# Initialize FastAPI Admin
@app.on_event("startup")
async def startup():
    await admin_factory.init(
        admin_app,
        engine,
        base_model=Base,
        providers=[
            UsernamePasswordProvider(username="admin", password="password"),
        ],
    )

@app.get("/items/")
async def read_items():
    return df.to_dict(orient="records")

# Include FastAPI admin routes
app.mount("/admin", admin_app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
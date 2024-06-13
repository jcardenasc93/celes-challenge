from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app.dataloader import load_data
from pandas import DataFrame


app_data = DataFrame()

@asynccontextmanager
async def load_app_data(app: FastAPI):
    """Loading parquet data to be used by the microservice"""
    app_data = load_data()
    yield

app = FastAPI(lifespan=load_app_data)

@app.get("/sales")
async def hello():
    return {"columns": list(app_data.columns)}

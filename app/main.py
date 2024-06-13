from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pandas import DataFrame
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.sales import router as sales_router
from app.dataloader import load_data
from app.schemas.base_response import BaseResponse

app_data = DataFrame()


@asynccontextmanager
async def load_app_data(app: FastAPI):
    """Loading parquet data to be used by the microservice"""
    app_data = load_data()
    yield


app = FastAPI(lifespan=load_app_data)
app.include_router(sales_router)


# App exceptions handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Creates HTTP exception handler in order to match with
    the microservice response schema
    """
    response = Response(
        content=BaseResponse(
            error_details=str(exc),
        ).model_dump_json(),
        status_code=exc.status_code,
    )
    response.headers["Content-Type"] = "application/json"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Creates validation exception handler in order to match with
    the microservice response schema
    """
    errors = jsonable_encoder(exc.errors())
    response = Response(
        content=BaseResponse(error_details=errors).model_dump_json(),
        status_code=status.HTTP_400_BAD_REQUEST,
    )
    response.headers["Content-Type"] = "application/json"
    return response


@app.get("/", status_code=204)
async def health_check():
    """Simple health check endpoint"""
    try:
        app_data = load_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

    return Response(status_code=204)

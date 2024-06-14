import logging
from contextlib import asynccontextmanager
from functools import cached_property, lru_cache
from typing import Callable, Dict, Optional, Sequence

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.dataloader import load_data
from app.schemas.base_response import BaseResponse

LOG_LEVELS_MAPPING = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "default": logging.INFO,
}


class AppSettings(BaseSettings):
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "DEBUG"
    FIREBASE_KEY_PATH: str = ""
    FIREBASE_API_KEY: str = ""
    FIREBASE_AUTH_DOMAIN: str = ""
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_STORAGE_BUCKET: str = ""
    FIREBASE_MSG_SENDER_ID: str = ""
    FIREBASE_APP_ID: str = ""
    ALLOWED_ORIGINS: str = ""

    @cached_property
    def APP_LOG_LEVEL(self) -> int:
        return LOG_LEVELS_MAPPING.get(self.LOG_LEVEL, LOG_LEVELS_MAPPING["default"])

    @cached_property
    def FIREBASE_APP_CONFIG(self) -> Dict[str, str]:
        app_config = {
            "apiKey": self.FIREBASE_API_KEY,
            "authDomain": self.FIREBASE_AUTH_DOMAIN,
            "projectId": self.FIREBASE_PROJECT_ID,
            "storageBucket": self.FIREBASE_STORAGE_BUCKET,
            "messagingSenderId": self.FIREBASE_MSG_SENDER_ID,
            "appId": self.FIREBASE_APP_ID,
            "databaseURL": "",
        }
        return app_config

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def app_settings() -> AppSettings:
    settings = AppSettings()
    return settings


def get_logger_handler():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(name)s | %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    return handler


logging.basicConfig(level=app_settings().APP_LOG_LEVEL)


@lru_cache
def get_logger() -> logging.Logger:
    logger = logging.getLogger("Sales logger")
    logger.addHandler(get_logger_handler())
    return logger


@asynccontextmanager
async def load_app_data(app: FastAPI):
    """Loading parquet data to be used by the microservice"""
    app_data = load_data()
    yield


def build_fastapi_app(dependencies: Optional[Sequence[Callable]] = None) -> FastAPI:
    app_dependencies = []
    if dependencies:
        app_dependencies = [Depends(f) for f in dependencies]

    app = FastAPI(
        title="Celes Sales microservice",
        dependencies=app_dependencies,
        description="Celes microservice to expose sales related data",
        responses={400: {"model": BaseResponse}, 404: {"model": BaseResponse}},
        lifespan=load_app_data,
    )

    settings = app_settings()
    if app_settings().ENVIRONMENT == "production":
        allow_all = settings.ALLOWED_ORIGINS.split(",")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_all,
            allow_credentials=True,
            allow_methods=allow_all,
            allow_headers=allow_all,
        )
    return app

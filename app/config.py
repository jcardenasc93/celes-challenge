import logging
from functools import cached_property, lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

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

    @cached_property
    def APP_LOG_LEVEL(self) -> int:
        return LOG_LEVELS_MAPPING.get(self.LOG_LEVEL, LOG_LEVELS_MAPPING["default"])

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

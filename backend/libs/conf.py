#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import lru_cache
from typing import Literal

from pip._internal.metadata.importlib._compat import BasePath

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{BasePath}/.env", env_file_encoding="utf-8", extra="ignore"
    )

    # Env Config
    ENVIRONMENT: Literal['dev', 'test', 'pro'] = 'dev'

    # Env MySQL
    DB_USERNAME: str = ""
    DB_PASSWORD: str = ""
    DB_HOST: str = ""
    DB_PORT: int = 3306
    DB_DATABASE: str = "test"
    DB_ECHO: bool = True
    DB_CHARSET: str = "utf8mb4"

    # Log
    LOG_ROOT_LEVEL: str = 'NOTSET'
    LOG_STDOUT_LEVEL: str = 'INFO'
    LOG_STD_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | '
        '<cyan> {correlation_id} </> | <lvl>{message}</>'
    )
    LOG_STDERR_LEVEL: str = 'ERROR'
    LOG_CID_DEFAULT_VALUE: str = '-'
    LOG_CID_UUID_LENGTH: int = 32  # must <= 32

    POLLING_INTERVAL_MILLISECONDS: int = 10 * 1000
    TASK_RETRY_COUNT: int = 3
    TASK_CONCURRENCY: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = Settings()

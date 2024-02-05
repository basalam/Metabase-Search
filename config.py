from enum import Enum
from typing import Any
from urllib.parse import quote

from brotli import MODE_TEXT, compress
from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBEngine(Enum):
    PG = "pg"


class CacheEngine(Enum):
    REDIS = "redis"
    MEMCACHED = "memcached"
    MEMORY = "memory"


class DBSettings(BaseModel):
    host: str
    port: str
    user: str
    password: str
    dbname: str
    engine: DBEngine = DBEngine.PG
    min_connections: int = 1
    max_connections: int = 25
    conn_str: None | str = None
    search_query: None | Any = None

    @model_validator(mode="before")
    def initialize(cls, values):
        with open("./search_query.sql", "rb") as f:
            values["search_query"] = compress(f.read(), mode=MODE_TEXT)

        password = quote(values["password"], safe="")
        user = quote(values["user"], safe="")
        values["conn_str"] = (
            f"postgres://{user}:{password}@{values['host']}:{values['port']}/{values['dbname']}"
        )
        return values


class MBSettings(BaseModel):
    base_url: str
    max_connections: int = 25


class CacheSettings(BaseModel):
    ttl: int = 600
    engine: CacheEngine = CacheEngine.MEMORY
    endpoint: str | None = None
    port: int | None = None
    db: int | None = None
    password: str | None = None
    pool_min_size: int | None = None
    pool_max_size: int | None = None


class Settings(BaseSettings):
    mb: MBSettings
    db: DBSettings
    cache: CacheSettings
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )


config = Settings()  # type: ignore

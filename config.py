from enum import Enum
from urllib.parse import quote

from brotli import MODE_TEXT, compress
from pydantic import BaseModel, BaseSettings, root_validator


class DBEngine(Enum):
    PG = "pg"


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
    search_query: None | str = None

    @root_validator
    def initialize(cls, values):
        with open("./search_query.sql", "rb") as f:
            values["search_query"] = compress(f.read(), mode=MODE_TEXT)

        password = quote(values["password"], safe="")
        user = quote(values["user"], safe="")
        values[
            "conn_str"
        ] = f"postgres://{user}:{password}@{values['host']}:{values['port']}/{values['dbname']}"
        return values


class MBSettings(BaseModel):
    base_url: str
    max_connections: int = 25


class Settings(BaseSettings):
    mb: MBSettings
    db: DBSettings
    cache_ttl: int = 600

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


config = Settings()  # type: ignore

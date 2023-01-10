import httpx
import brotli
import asyncpg
from lib.hermes import Hermes
from typing import Any, List, Dict
from fastapi import FastAPI, Header
from fastapi.exceptions import HTTPException
from fastapi.responses import ORJSONResponse, Response
from lib.hermes.backend.dict import Backend as cacheBackend
from pydantic import BaseSettings, BaseModel, root_validator
from urllib.parse import quote


class DBSettings(BaseModel):
    host: str
    port: str
    user: str
    password: str
    dbname: str
    min_connections: int = 1
    max_connections: int = 25
    conn_str: None | str = None
    search_query: None | str = None

    @root_validator
    def initialize(cls, values):
        with open("./search_query.sql", "rb") as f:
            values["search_query"] = brotli.compress(f.read(), mode=brotli.MODE_TEXT)

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


class MyFastAPI(FastAPI):
    search_query: str | None = None
    conn_pool: asyncpg.Pool
    mb_client: httpx.AsyncClient


dict_cache = Hermes(cacheBackend, ttl=0)
app = MyFastAPI(title="Metabase Search", default_response_class=ORJSONResponse)


@dict_cache(
    ttl=config.cache_ttl,
    key=lambda cookie: brotli.compress(
        str.encode(cookie),
        mode=brotli.MODE_TEXT,
    ),
)
async def get_mb_user(cookie: str):
    return await app.mb_client.get("/api/user/current", headers={"Cookie": cookie})


@app.on_event("startup")
async def init_reqs():
    app.mb_client = httpx.AsyncClient(
        limits=httpx.Limits(
            max_connections=config.mb.max_connections,
            max_keepalive_connections=config.mb.max_connections,
        ),
        base_url=config.mb.base_url,
        http2=True,
    )

    conn_pool = await asyncpg.create_pool(
        config.db.conn_str,
        min_size=config.db.min_connections,
        max_size=config.db.max_connections,
    )

    if conn_pool:
        app.conn_pool = conn_pool

    else:
        raise Exception("Connection is None.")


@dict_cache(ttl=config.cache_ttl)
@app.get("/api/search")
async def search(
    q: str,
    archived: str = "FALSE",
    table_db_id: int | None = None,
    models: str | None = None,
    limit: int = 50,
    offset: int = 0,
    cookie: str = Header(),
):
    archived = archived.upper()
    if archived not in ["TRUE", "FALSE"]:
        raise HTTPException(status_code=400, detail="Archived should be true or false")
    r = await get_mb_user(cookie=cookie)
    if r.status_code not in range(200, 300):
        get_mb_user.invalidate(cookie=cookie)
        return Response(r.content, r.status_code, headers=r.headers)
    user_id = r.json()["id"]
    async with app.conn_pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetch(
                brotli.decompress(config.db.search_query)
                .decode("utf-8")
                .replace("SEARCH_TERM", "'%" + q + "%'")
                .replace("QUERY_LIMIT", str(limit))
                .replace("QUERY_OFFSET", str(offset))
                .replace("SEARCH_ARCHIVED", archived)
                .replace("USER_ID", str(user_id))
            )
            available_models = []
            final_result: List[dict] = []
            models_arr = None
            for i in result:
                current: Dict[str, Any] = dict(i)
                if current["model"] not in available_models:
                    available_models.append(current["model"])

                current["collection"] = {}
                for k, v in i.items():
                    if k.startswith("collection_"):
                        current.pop(k)
                        current["collection"][k.replace("collection_", "")] = v

                is_db_valid = True
                if table_db_id:
                    if current["database_id"] != table_db_id:
                        is_db_valid = False

                is_model_valid = True
                if models:
                    models_arr = models.split(",")
                    is_model_valid = False
                    for m in models_arr:
                        if current["model"] == m:
                            is_model_valid = True

                is_valid = is_db_valid and is_model_valid

                if is_valid:
                    final_result.append(current)

            return ORJSONResponse(
                {
                    "total": len(final_result),
                    "limit": limit,
                    "offset": offset,
                    "table_db_id": table_db_id,
                    "models": models_arr,
                    "available_models": available_models,
                    "data": final_result,
                }
            )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", reload=True)

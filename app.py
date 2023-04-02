from typing import List

import asyncpg
import httpx
import orjson
from brotli import MODE_TEXT, compress, decompress
from fastapi import FastAPI, Header
from fastapi.exceptions import HTTPException
from fastapi.responses import ORJSONResponse, Response

from config import config, CacheEngine
from database import add_filter, generate_query
from aiocache import cached, AIOCACHE_CACHES
from aiocache.base import BaseCache
from aiocache.backends.memory import SimpleMemoryCache
from aiocache.backends.redis import RedisCache
from aiocache.backends.memcached import MemcachedCache
from aiocache.serializers import BaseSerializer


class BrotliSerializer(BaseSerializer):
    DEFAULT_ENCODING = None

    def __init__(self, *args, mode=MODE_TEXT, encoding="utf-8", **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = mode
        self.encoding = encoding

    def dumps(self, value):
        if isinstance(value, httpx.Response):
            return compress(
                orjson.dumps(value.json()),
                mode=self.mode,
            )

    def loads(self, value):
        if value is None:
            return None
        return decompress(value).decode(self.encoding)  # noqa: S301


class MyFastAPI(FastAPI):
    search_query: str | None = None
    conn_pool: asyncpg.Pool
    mb_client: httpx.AsyncClient


def cookie_cache_key_builder(func, cookie):
    return compress(str.encode(cookie, encoding="utf-8"), mode=MODE_TEXT)


def brotli_cache_key_from_args(self, func, args, kwargs):
    ordered_kwargs = sorted(kwargs.items())
    key = (
        (func.__module__ or "")
        + func.__name__
        + str(args[1:] if self.noself else args)
        + str(ordered_kwargs)
    )
    return compress(str.encode(key, encoding="utf-8"), mode=MODE_TEXT)


cache_backend: BaseCache = BaseCache()
cache_kwargs: dict = {}
match config.cache.engine:
    case CacheEngine.MEMORY:
        cache_kwargs: dict = {
            "namespace": "main",
        }
        cache_backend = SimpleMemoryCache(serializer=BrotliSerializer(), **cache_kwargs)
    case CacheEngine.REDIS:
        cache_kwargs = {
            "endpoint": config.cache.endpoint,
            "port": config.cache.port,
            "db": config.cache.db,
            "password": config.cache.password,
            "pool_min_size": config.cache.pool_min_size,
            "pool_max_size": config.cache.pool_max_size,
            "namespace": "main",
        }
        cache_backend = RedisCache(serializer=BrotliSerializer(), **cache_kwargs)
    case CacheEngine.MEMCACHED:
        cache_kwargs = {
            "endpoint": config.cache.endpoint,
            "port": config.cache.port,
            "pool_size": config.cache.pool_max_size,
            "namespace": "main",
        }
        cache_backend = MemcachedCache(serializer=BrotliSerializer(), **cache_kwargs)
    case default:
        raise Exception("Invalid Cache Engine.!")

app = MyFastAPI(title="Metabase Search", default_response_class=ORJSONResponse)


@cached(
    ttl=config.cache.ttl,
    cache=AIOCACHE_CACHES[cache_backend.NAME],
    serializer=BrotliSerializer(),
    key_builder=cookie_cache_key_builder,
    **cache_kwargs,
)
async def get_mb_user(cookie: str) -> httpx.Response:
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
        raise Exception("Connection Pool is None.")


@cached(
    ttl=config.cache.ttl,
    cache=AIOCACHE_CACHES[cache_backend.NAME],
    serializer=BrotliSerializer(),
    key_builder=brotli_cache_key_from_args,
    **cache_kwargs,
)
@app.get("/api/search")
async def search(
    q: str,
    archived: str = "FALSE",
    table_db_id: int | None = None,
    models: List[str] | None = None,
    limit: int = 50,
    offset: int = 0,
    cookie: str = Header(),
):
    if len(q) < 3:
        return ORJSONResponse(
            {
                "total": 0,
                "limit": limit,
                "offset": offset,
                "table_db_id": table_db_id,
                "models": models,
                "available_models": [],
                "data": [],
            }
        )
    conditions: str = ""
    archived = archived.upper()
    if archived not in ["TRUE", "FALSE"]:
        raise HTTPException(status_code=400, detail="Archived should be true or false")
    r: str | httpx.Response = await get_mb_user(cookie=cookie)
    resp: dict = {}
    if isinstance(r, httpx.Response):
        if r.status_code not in range(200, 300):
            await cache_backend.delete(key=decompress(cookie).decode("utf-8"))
            return Response(r.content, r.status_code, headers=r.headers)
        resp = r.json()
    elif isinstance(r, str):
        resp = orjson.loads(r)

    user_id: int = resp["id"]
    if models is not None:
        qouted_models: List[str] = []
        for model in models:
            qouted_models.append(f"'{model.strip()}'")
        if len(qouted_models) > 0:
            conditions = add_filter(
                conditions, f'"model" in ({",".join(qouted_models)})', "AND"
            )
    if table_db_id is not None:
        conditions = add_filter(conditions, f'"database_id" = {table_db_id}', "AND")
    async with app.conn_pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetch(
                generate_query(
                    q=q,
                    limit=limit,
                    offset=offset,
                    archived=archived,
                    user_id=user_id,
                    conditions=conditions,
                )
            )
            available_models = []
            final_result: List[dict] = []
            for i in result:
                current = {
                    "description": i["description"],
                    "archived": i["archived"],
                    "collection_position": i["collection_position"],
                    "table_id": i["table_id"],
                    "bookmark": i["bookmark"],
                    "database_id": i["database_id"],
                    "name": i["name"],
                    "app_id": i["app_id"],
                    "table_schema": i["table_schema"],
                    "collection_authority_level": i["collection_authority_level"],
                    "updated_at": i["updated_at"],
                    "moderated_status": i["moderated_status"],
                    "dataset_query": i["dataset_query"],
                    "id": i["id"],
                    "table_description": i["table_description"],
                    "dashboardcard_count": i["dashboardcard_count"],
                    "initial_sync_status": i["initial_sync_status"],
                    "table_name": i["table_name"],
                    "model": i["model"],
                    "collection": {
                        k.replace("collection_", ""): v
                        for k, v in i.items()
                        if k.startswith("collection_")
                    },
                }
                if current["model"] not in available_models:
                    available_models.append(current["model"])
                final_result.append(current)

            return ORJSONResponse(
                {
                    "total": len(final_result),
                    "limit": limit,
                    "offset": offset,
                    "table_db_id": table_db_id,
                    "models": models,
                    "available_models": available_models,
                    "data": final_result,
                }
            )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", reload=True)

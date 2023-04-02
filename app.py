from typing import Any, Dict, List

import asyncpg
import httpx
import orjson
from brotli import MODE_TEXT, compress, decompress
from fastapi import FastAPI, Header
from fastapi.exceptions import HTTPException
from fastapi.responses import ORJSONResponse, Response

from config import config
from database import add_filter, generate_query
from aiocache import Cache, cached
from aiocache.serializers import PickleSerializer, BaseSerializer


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


cache = Cache(Cache.MEMORY, namespace="main")
cache.serializer = BrotliSerializer()
app = MyFastAPI(title="Metabase Search", default_response_class=ORJSONResponse)


@cached(
    ttl=config.cache_ttl,
    cache=Cache.MEMORY,
    serializer=BrotliSerializer(),
    key_builder=cookie_cache_key_builder,
    namespace="main",
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
        raise Exception("Connection is None.")


@cached(
    ttl=config.cache_ttl,
    cache=Cache.MEMORY,
    serializer=PickleSerializer(),
    namespace="main",
    key_builder=brotli_cache_key_from_args,
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
    conditions: str = ""
    archived = archived.upper()
    if archived not in ["TRUE", "FALSE"]:
        raise HTTPException(status_code=400, detail="Archived should be true or false")
    r: str | httpx.Response = await get_mb_user(cookie=cookie)
    resp: dict = {}
    if isinstance(r, httpx.Response):
        if r.status_code not in range(200, 300):
            await cache.delete(key=decompress(cookie).decode("utf-8"))
            return Response(r.content, r.status_code, headers=r.headers)
        resp = r.json()
    if isinstance(r, str):
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
                current: Dict[str, Any] = dict(i)
                if current["model"] not in available_models:
                    available_models.append(current["model"])

                current["collection"] = {}
                for k, v in i.items():
                    if k.startswith("collection_"):
                        current.pop(k)
                        current["collection"][k.replace("collection_", "")] = v
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

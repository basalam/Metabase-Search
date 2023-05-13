# Metabase Search

Better searching for [metabase](https://github.com/metabase/metabase/)

## How it works?

We are running the same query as metabase but faster and no bugs

the goal is to reach a response that look likes `sample.json` file

## Metabase Version

We try to support the latest version of metabase but here we have a table that you can get help from it for selecting docker tag (if you are not using Docker use provided DockerTag as CommitHash when cloning/checking-out) ["X" Means every number could be there]

| DockerTag | Tested Metabase version |
-|-
|3721849|v0.45.X|
|5498835|v0.46.X|

### With the help of

- asyncpg
- brotli
- fastapi (with orjson)
- httpx (with http2 and brotli enabled)
- aiocache (customized)
- pydantic

At every request we are sending a request to metabase current user api to verify the user and also getting the user_id (don't worry we are caching that response for 10 minutes)

it accepts whatever metabase frontend sends and will act just like normal metabase search api

it has a connection pool from 1 to 25 number of connections and keep-alive connections to metabase api (for user data and authentication)

and will read the `search_query.sql` file and compress that using brotli for better performance and less memory usage

also we are caching search result for 10 minutes

## How to use

First of all I recommend to run `gin_index.sql` file inside your PostgreSQL, it will make your db faster when running `LIKE` queries

> It will make PostgreSQL Memory usage higher (Also don't forget to increase SHM Size if you are running your PostgreSQL inside Docker without that you will get some low space on device errors)

Just deploy it like a normal fastapi project

> You need python 3.11 or higher to run this project (That's a bit crazy, but we are using some pretty typing features)
>
> maximum number of connections to db = number of project replicas \* (number of uvicorn workers \* 25)

and point the `/api/search` location to this project

> no rewrite needed when using reverse proxy (if your metabase is not in subpath)

Environment Variables (Case insensitive):

```.env
# base URL of Metabase
MB__BASE_URL
# Maximum number of connections to Metabase HTTP API (for user info) (defualts to 25)
MB__MAX_CONNECTIONS
# Host name for database (Could be a readonly address)
DB__HOST
# Port number for database (Could be a readonly port)
DB__PORT
# Username for database connection (Could be a readonly user)
DB__USER
# Password for database connection
DB__PASSWORD
# Name of the database
DB__DBNAME
# Minimum number of connections to database (defualts to 1)
DB__MIN_CONNECTIONS
# Maximum number of connections to database (defualts to 25)
DB__MAX_CONNECTIONS
# Database Engine (for now only pg is supported) (defualts to 'pg')
DB__ENGINE
# Time-To-Live for caches in second (search and user info) (defualts to 600)
CACHE__TTL
# Engine for caches (one of redis, memcached or memory) (defualts to memory)
CACHE__ENGINE
# Endpoint for caches (for example: 127.0.0.1) (defualts to None)
CACHE__ENDPOINT
# Port for caches (for example: 6379) (defualts to None)
CACHE__PORT
# DB for caches (for example: 0) (defualts to None)
CACHE__DB
# DB for caches (for example: 3ecr&t) (defualts to None)
CACHE__PASSWORD
# Minimum size for cache connection pool (for example: 1) (defualts to None)
CACHE__POOL_MIN_SIZE
# Maximum size for cache connection pool (for example: 12) (defualts to None)
CACHE__POOL_MAX_SIZE
```

**Storngly Recommended** You can checkout [deploy](./deploy) directory to see a full example of how to deploy this using `docker-compose` and NginX near a real metabase

## Contributing

Feel free to contribute to open new PRs to this project

We are using `black` formatter as python formatter and some other linters, checkers and fixers that you can find them at [.pre-commit-config.yaml](.pre-commit-config.yaml) file

I would recommend to use `pre-commit`

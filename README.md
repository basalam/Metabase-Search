# Metabase Search

Better searching for [metabase](https://github.com/metabase/metabase/)

## How it works?

We are running the same query as metabase but faster and no bugs

the goal is to reach a response that look likes `sample.json` file

### With the help of

- asyncpg
- brotli
- fastapi (with orjson)
- httpx (with http2 and brotli enabled)
- hermes cache (customized)

At every request we are sending a request to metabase current user api to verify the user and also getting the user_id (don't worry we are caching that response for 10 minutes)

it accepts whatever metabase frontend sends and will act just like normal metabase search api

it has a connection pool from 1 to 25 number of connections and keep-alive connections to metabase api (for user data and authentication)

and will read the `search_query.sql` file and compress that using brotli for better performance and less memory usage

also we are caching search result for 10 minutes

## How to use

First of all I recommend to run `gin_index.sql` file inside your PostgreSQL, it will make your db faster when running `like` queries

> It will make postgresql Memory usage higher

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
CACHE_TTL
```

**Storngly Recommended** You can checkout [deploy](./deploy) directory to see a full example of how to deploy this using `docker-compose` and NginX near a real metabase

## Contributing

Feel free to contribute to open new PRs to this project

We are using `black` formatter as python formatter and some other linters, checkers and fixers that you can find them at [.pre-commit-config.yaml](.pre-commit-config.yaml) file

I would recommend to use `pre-commit`

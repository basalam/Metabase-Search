#!/bin/bash

bash -c 'cd /search; PORT=9090 MB__BASE_URL=http://localhost gunicorn -k "uvicorn.workers.UvicornWorker" -c "/search/gunicorn_conf.py" "app:app"' &
/metabase/run_metabase.sh &
nginx -g "daemon off;" &

wait -n

exit $?

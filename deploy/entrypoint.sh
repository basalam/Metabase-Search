#!/bin/bash

# Start each proccess in backgroud
bash -c 'cd /search; PORT=9090 MB__BASE_URL=http://localhost gunicorn -k "uvicorn.workers.UvicornWorker" -c "/search/gunicorn_conf.py" "app:app"' &
/metabase/run_metabase.sh &
nginx -g "daemon off;" &

# Wait for first one to kill
wait -n

# Close script with correct exit code
exit $?

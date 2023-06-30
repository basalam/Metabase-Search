FROM metabase/metabase:v0.46.0 AS metabase
FROM tiangolo/uvicorn-gunicorn:python3.11 AS uvicorn-gunicorn

FROM nginx:mainline-bookworm AS runtime

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH: "${PYTHONPATH}:/search"

RUN apt-get update && \
  apt-get install -y default-jre-headless python3 python-is-python3 python3-pip && \
  apt-get clean

RUN pip install --break-system-packages uvicorn[standard] gunicorn

RUN useradd -ms /bin/bash metabase --uid 2000

COPY --from=uvicorn-gunicorn /gunicorn_conf.py /search/gunicorn_conf.py
COPY --from=metabase /app /metabase
RUN mkdir -p /plugins && chown -R metabase:metabase /plugins
RUN bash -c "sed -i 's/\/app/\/metabase/g' /metabase/run_metabase.sh"

COPY requirements.txt /search/requirements.txt
RUN pip install --break-system-packages -r /search/requirements.txt
COPY . /search

COPY deploy/nginx.conf /etc/nginx/nginx.conf
COPY deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT /entrypoint.sh

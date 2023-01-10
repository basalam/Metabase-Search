FROM tiangolo/uvicorn-gunicorn:python3.11

ENV PYTHONUNBUFFERED 1
ENV VARIABLE_NAME app
ENV MODULE_NAME app
ENV APP_MODULE app:app
ENV PYTHONPATH: "${PYTHONPATH}:$(pwd)"

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

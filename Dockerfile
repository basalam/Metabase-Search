FROM tiangolo/uvicorn-gunicorn:python3.10

ENV PYTHONUNBUFFERED 1
ENV VARIABLE_NAME app
ENV MODULE_NAME app
ENV APP_MODULE app:app
ENV TZ=Asia/Tehran
ENV PYTHONPATH: "${PYTHONPATH}:$(pwd)"

WORKDIR /app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

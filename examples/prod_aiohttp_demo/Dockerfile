FROM python:3.8-alpine as base

FROM base as builder
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev openssl-dev make postgresql-dev
RUN pip install poetry==1.0.5
COPY . /src/
WORKDIR /src
RUN python -m venv /env && . /env/bin/activate && poetry install

FROM base
RUN apk add --no-cache postgresql-libs
COPY --from=builder /env /env
COPY --from=builder /src /src
WORKDIR /src
CMD ["/env/bin/gunicorn", "gino_aiohttp_demo.main:async_app", "-b", "0.0.0.0:80", "-k", "aiohttp.GunicornWebWorker"]

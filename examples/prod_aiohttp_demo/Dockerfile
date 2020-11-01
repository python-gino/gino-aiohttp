FROM python:3.9-alpine as base

FROM base as builder
RUN apk add --no-cache --virtual .build-deps curl gcc musl-dev libffi-dev openssl-dev make postgresql-dev
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
COPY . /src/
WORKDIR /src
RUN python -m venv /env && . /env/bin/activate && $HOME/.poetry/bin/poetry install

FROM base
RUN apk add --no-cache postgresql-libs
COPY --from=builder /env /env
COPY --from=builder /src /src
WORKDIR /src
CMD ["/env/bin/gunicorn", "gino_aiohttp_demo.main:async_app", "-b", "0.0.0.0:80", "-k", "aiohttp.GunicornWebWorker"]

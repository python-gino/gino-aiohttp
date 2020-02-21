# gino-aiohttp

## Introduction

An extension for GINO to support aiohttp.web server.

## Usage

The common usage looks like this:

```python
    from aiohttp import web
    from gino.ext.aiohttp import Gino

    db = Gino()
    app = web.Application(middlewares=[db])
    db.init_app(app)
```

## Configuration

By `init_app()` method GINO subscribes to a few signals on aiohttp, so that
GINO could use database configuration to initialize the bound engine.

The configuration can be passed in the `config` parameter of
`init_app`, or if that is not set, in `app['config']['gino']`, both of
which should be a dictionary.

The config includes:

| Name            | Description                                                                                                       | Default     |
| --------------- | ----------------------------------------------------------------------------------------------------------------- | ----------- |
| `driver`        | the database driver                                                                                               | `asyncpg`   |
| `host`          | database server host                                                                                              | `localhost` |
| `port`          | database server port                                                                                              | `5432`      |
| `user`          | database server user                                                                                              | `postgres`  |
| `password`      | database server password                                                                                          | empty       |
| `database`      | database name                                                                                                     | `postgres`  |
| `dsn`           | a SQLAlchemy database URL to create the engine, its existence will replace all previous connect arguments.        | N/A         |
| `pool_min_size` | the initial number of connections of the db pool.                                                                 | N/A         |
| `pool_max_size` | the maximum number of connections in the db pool.                                                                 | N/A         |
| `echo`          | enable SQLAlchemy echo mode.                                                                                      | N/A         |
| `ssl`           | SSL context passed to `asyncpg.connect`.                                                                          | `None`      |
| `kwargs`        | other parameters passed to the specified dialects, like `asyncpg`. Unrecognized parameters will cause exceptions. | N/A         |

## Lazy Connection

If the `db` is set as an aiohttp middleware, then a lazy connection is
available at `request['connection']`. By default, a database connection
is borrowed on the first query, shared in the same execution context, and
returned to the pool on response. If you need to release the connection
early in the middle to do some long-running tasks, you can simply do this:

```python
    await request['connection'].release(permanent=False)
```

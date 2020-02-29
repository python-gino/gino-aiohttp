# noinspection PyPackageRequirements
import asyncio
import logging

import click
from aiohttp.web import HTTPNotFound, middleware
from sqlalchemy.engine.url import URL

from gino.api import Gino as _Gino
from gino.api import GinoExecutor as _Executor
from gino.engine import GinoConnection as _Connection
from gino.engine import GinoEngine as _Engine
from gino.strategies import GinoStrategy

logger = logging.getLogger("gino.ext.aiohttp")


class AiohttpModelMixin:
    @classmethod
    async def get_or_404(cls, *args, **kwargs):
        # noinspection PyUnresolvedReferences
        rv = await cls.get(*args, **kwargs)
        if rv is None:
            raise HTTPNotFound(reason="{} is not found".format(cls.__name__))
        return rv


# noinspection PyClassHasNoInit
class GinoExecutor(_Executor):
    async def first_or_404(self, *args, **kwargs):
        rv = await self.first(*args, **kwargs)
        if rv is None:
            raise HTTPNotFound(reason="No such data")
        return rv


# noinspection PyClassHasNoInit
class GinoConnection(_Connection):
    async def first_or_404(self, *args, **kwargs):
        rv = await self.first(*args, **kwargs)
        if rv is None:
            raise HTTPNotFound(reason="No such data")
        return rv


# noinspection PyClassHasNoInit
class GinoEngine(_Engine):
    connection_cls = GinoConnection

    async def first_or_404(self, *args, **kwargs):
        rv = await self.first(*args, **kwargs)
        if rv is None:
            raise HTTPNotFound(reason="No such data")
        return rv


class AiohttpStrategy(GinoStrategy):
    name = "aiohttp"
    engine_cls = GinoEngine


AiohttpStrategy()


@middleware
class Gino(_Gino):
    """Support aiohttp.web server.

    The common usage looks like this::

        from aiohttp import web
        from gino.ext.aiohttp import Gino

        db = Gino()
        app = web.Application(middlewares=[db])
        db.init_app(app)

    By :meth:`init_app` GINO subscribes to a few signals on aiohttp, so that
    GINO could use database configuration to initialize the bound engine.

    The configuration can be passed in the ``config`` parameter of
    ``init_app``, or if that is not set, in app['config']['gino'], both of
    which should be a dictionary.

    The config includes:

    * ``driver`` - the database driver, default is ``asyncpg``.
    * ``host`` - database server host, default is ``localhost``.
    * ``port`` - database server port, default is ``5432``.
    * ``user`` - database server user, default is ``postgres``.
    * ``password`` - database server password, default is empty.
    * ``database`` - database name, default is ``postgres``.
    * ``dsn`` - a SQLAlchemy database URL to create the engine, its existence
      will replace all previous connect arguments.
    * ``pool_min_size`` - the initial number of connections of the db pool.
    * ``pool_max_size`` - the maximum number of connections in the db pool.
    * ``echo`` - enable SQLAlchemy echo mode.
    * ``ssl`` - SSL context passed to ``asyncpg.connect``, default is ``None``.
    * ``kwargs`` - other parameters passed to the specified dialects,
      like ``asyncpg``. Unrecognized parameters will cause exceptions.

    If the ``db`` is set as an aiohttp middleware, then a lazy connection is
    available at ``request['connection']``. By default, a database connection
    is borrowed on the first query, shared in the same execution context, and
    returned to the pool on response. If you need to release the connection
    early in the middle to do some long-running tasks, you can simply do this::

        await request['connection'].release(permanent=False)

    """

    model_base_classes = _Gino.model_base_classes + (AiohttpModelMixin,)
    query_executor = GinoExecutor

    def __call__(self, request, handler):
        return self._middleware(request, handler)

    async def _middleware(self, request, handler):
        async with self.acquire(lazy=True) as connection:
            request["connection"] = connection
            try:
                return await handler(request)
            finally:
                request.pop("connection", None)

    def init_app(self, app, config=None, *, db_attr_name="db"):
        app[db_attr_name] = self

        if not isinstance(config, dict):
            self.config = app["config"].get("gino", {})
        else:
            self.config = config.copy()

        async def before_server_start(_):
            if "dsn" in self.config:
                dsn = self.config["dsn"]
            else:
                dsn = URL(
                    drivername=self.config.setdefault("driver", "asyncpg"),
                    host=self.config.setdefault("host", "localhost"),
                    port=self.config.setdefault("port", 5432),
                    username=self.config.setdefault("user", "postgres"),
                    password=self.config.setdefault("password", ""),
                    database=self.config.setdefault("database", "postgres"),
                )

            await self.set_bind(
                dsn,
                echo=self.config.setdefault("echo", False),
                min_size=self.config.setdefault("pool_min_size", 5),
                max_size=self.config.setdefault("pool_max_size", 10),
                ssl=self.config.setdefault("ssl"),
                **self.config.setdefault("kwargs", dict()),
            )
            msg = "Database connected: "
            logger.info(
                msg + format_engine(self.bind),
                extra={
                    "color_message": msg + format_engine(self.bind, color=True)
                },
            )

        async def after_server_stop(_):
            msg = "Closing database connection: "
            logger.info(
                msg + format_engine(self.bind),
                extra={
                    "color_message": msg + format_engine(self.bind, color=True)
                },
            )
            _bind = self.pop_bind()
            await _bind.close()
            msg = "Closed database connection: "
            logger.info(
                msg + format_engine(_bind),
                extra={"color_message": msg + format_engine(_bind, color=True)},
            )

        app.on_startup.append(before_server_start)
        app.on_cleanup.append(after_server_stop)

    async def first_or_404(self, *args, **kwargs):
        rv = await self.first(*args, **kwargs)
        if rv is None:
            raise HTTPNotFound(reason="No such data")
        return rv

    async def set_bind(self, bind, **kwargs):
        kwargs.setdefault("strategy", "aiohttp")
        for retries in range(self.config.setdefault("retry_times", 5)):
            try:
                if retries == 0:
                    logger.info("Connecting to database...")
                else:
                    logger.info("Retrying to connect to database...")
                return await super().set_bind(bind, **kwargs)
            except ConnectionError:
                logger.info(
                    f"Waiting {self.config.setdefault('retry_interval',5)}s to reconnect..."
                )
                await asyncio.sleep(self.config["retry_interval"])
        logger.error("Max retries reached.")
        raise ConnectionError("Database connection error!")


def format_engine(engine, color=False):
    if color:
        return "<{classname} max={max} min={min} cur={cur} use={use}>".format(
            classname=click.style(
                engine.raw_pool.__class__.__module__
                + "."
                + engine.raw_pool.__class__.__name__,
                fg="green",
            ),
            max=click.style(repr(engine.raw_pool._maxsize), fg="cyan"),
            min=click.style(repr(engine.raw_pool._minsize), fg="cyan"),
            cur=click.style(
                repr(
                    len(
                        [
                            0
                            for con in engine.raw_pool._holders
                            if con._con and not con._con.is_closed()
                        ]
                    )
                ),
                fg="cyan",
            ),
            use=click.style(
                repr(
                    len([0 for con in engine.raw_pool._holders if con._in_use])
                ),
                fg="cyan",
            ),
        )
    else:
        # noinspection PyProtectedMember
        return "<{classname} max={max} min={min} cur={cur} use={use}>".format(
            classname=engine.raw_pool.__class__.__module__
            + "."
            + engine.raw_pool.__class__.__name__,
            max=engine.raw_pool._maxsize,
            min=engine.raw_pool._minsize,
            cur=len(
                [
                    0
                    for con in engine.raw_pool._holders
                    if con._con and not con._con.is_closed()
                ]
            ),
            use=len([0 for con in engine.raw_pool._holders if con._in_use]),
        )

import logging

import click
from aiohttp import web

from . import config
from .models import db

try:
    from importlib.metadata import entry_points
except ImportError:  # pragma: no cover
    from importlib_metadata import entry_points

logger = logging.getLogger(__name__)


async def async_app():
    return get_app()


def get_app():
    app = web.Application(middlewares=[db])
    db.init_app(
        app,
        dict(
            dsn=config.DB_DSN,
            echo=config.DB_ECHO,
            min_size=config.DB_POOL_MIN_SIZE,
            max_size=config.DB_POOL_MAX_SIZE,
            ssl=config.DB_SSL,
            retry_limit=config.DB_RETRY_LIMIT,
            retry_interval=config.DB_RETRY_INTERVAL,
            kwargs=config.DB_KWARGS,
        ),
    )
    load_modules(app)
    return app


def load_modules(app=None):
    for ep in entry_points()["gino_aiohttp_demo.modules"]:
        logger.info(
            "Loading module: %s",
            ep.name,
            extra={"color_message": "Loading module: " + click.style("%s", fg="cyan")},
        )
        mod = ep.load()
        if app:
            init_app = getattr(mod, "init_app", None)
            if init_app:
                init_app(app)

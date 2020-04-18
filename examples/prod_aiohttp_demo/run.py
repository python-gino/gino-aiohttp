import os

from aiohttp import web
from gino_aiohttp_demo import main

if __name__ == "__main__":
    app = main.get_app()
    web.run_app(
        app,
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", "5000")),
    )

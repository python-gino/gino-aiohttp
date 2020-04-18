import asyncio

import pytest
from aiohttp.test_utils import TestClient, TestServer

pytestmark = pytest.mark.asyncio
_MAX_INACTIVE_CONNECTION_LIFETIME = 59.0


async def _test_index_returns_200(app):
    async with TestClient(TestServer(app)) as client:
        response = await client.get("/")
        assert response.status == 200
        assert await response.text() == "Hello, world!"


async def test_index_returns_200(app):
    await _test_index_returns_200(app)


async def test_index_returns_200_dsn(app_dsn):
    await _test_index_returns_200(app_dsn)


async def _test(app):
    async with TestClient(TestServer(app)) as client:
        response = await client.get("/users/1")
        assert response.status == 404

        for method in "1234":
            response = await client.get("/users/1?method=" + method)
            assert response.status == 404

        response = await client.post("/users", data=dict(name="fantix"))
        assert response.status == 200
        assert await response.json() == dict(id=1, nickname="fantix")

        response = await client.get("/users/1")
        assert response.status == 200
        assert await response.json() == dict(id=1, nickname="fantix")


async def test(app):
    await _test(app)


async def test_dsn(app_dsn):
    await _test(app_dsn)


async def test_ssl(app_ssl):
    await _test(app_ssl)


async def test_db_delayed(app_db_delayed):
    loop = asyncio.get_event_loop()
    loop.call_later(1, loop.create_task, app_db_delayed.start_proxy())
    await _test(app_db_delayed)

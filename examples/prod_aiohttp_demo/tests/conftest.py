import pytest
from aiohttp.test_utils import TestClient, TestServer
from alembic.config import main
from async_generator import yield_, async_generator
from gino_aiohttp_demo.main import get_app


@pytest.fixture
@async_generator
async def client():
    main(["--raiseerr", "upgrade", "head"])
    async with TestClient(TestServer(get_app())) as client:
        await yield_(client)
    main(["--raiseerr", "downgrade", "base"])

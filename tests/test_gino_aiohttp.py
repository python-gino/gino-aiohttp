import pytest

pytestmark = pytest.mark.asyncio


async def _test_index_returns_200(test_client):
    response = await test_client.get("/")
    assert response.status == 200
    assert await response.text() == "Hello, world!"


async def test_index_returns_200(test_client):
    await _test_index_returns_200(test_client)


async def test_index_returns_200_dsn(test_client_dsn):
    await _test_index_returns_200(test_client_dsn)


async def _test(test_client):
    response = await test_client.get("/users/1")
    assert response.status == 404

    for method in "1234":
        response = await test_client.get("/users/1?method=" + method)
        assert response.status == 404

    response = await test_client.post("/users", data=dict(name="fantix"))
    assert response.status == 200
    assert await response.json() == dict(id=1, nickname="fantix")

    response = await test_client.get("/users/1")
    assert response.status == 200
    assert await response.json() == dict(id=1, nickname="fantix")


async def test(test_client):
    await _test(test_client)


async def test_dsn(test_client_dsn):
    await _test(test_client_dsn)


async def test_ssl(test_client_ssl):
    await _test(test_client_ssl)

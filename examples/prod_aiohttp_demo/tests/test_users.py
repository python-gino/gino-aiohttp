import uuid

import pytest

pytestmark = pytest.mark.asyncio


async def test_crud(client):
    assert (await client.get("/users/1")).status == 404
    nickname = str(uuid.uuid4())
    r = await client.post("/users", json=dict(name=nickname))
    assert r.status == 200
    r = await r.json()

    r = await client.get("/users/{}".format(r["id"]))
    assert r.status == 200
    assert (await r.json())["nickname"] == nickname

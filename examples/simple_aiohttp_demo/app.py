import os
from aiohttp import web
from gino.ext.aiohttp import Gino


DB_ARGS = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 5432),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASS", ""),
    database=os.getenv("DB_NAME", "postgres"),
)
PG_URL = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
    **DB_ARGS
)

db = Gino()
app = web.Application(middlewares=[db])
config = {"dsn": PG_URL}
db.init_app(app, config=config)


class User(db.Model):
    __tablename__ = "gino_users"

    id = db.Column(db.BigInteger(), primary_key=True)
    nickname = db.Column("name", db.Unicode(), default="unnamed")


routes = web.RouteTableDef()


@routes.get("/")
async def root(request):
    return web.Response(text="Hello, world!")


@routes.get("/users/{uid}")
async def get_user(request):
    uid = int(request.match_info["uid"])
    return web.json_response((await User.get_or_404(uid)).to_dict())


@routes.post("/users")
async def add_user(request):
    form = await request.post()
    u = await User.create(nickname=form.get("name"))
    return web.json_response(u.to_dict())


app.router.add_routes(routes)


async def create():
    await db.set_bind(PG_URL)
    await db.gino.create_all()
    await db.pop_bind().close()


if __name__ == "__main__":
    import asyncio

    asyncio.get_event_loop().run_until_complete(create())
    web.run_app(app)

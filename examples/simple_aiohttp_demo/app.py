import os

from aiohttp import web
from gino.ext.aiohttp import Gino

# Database Configuration
PG_URL = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 5432),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_DATABASE", "postgres"),
)

# Initialize Gino instance
db = Gino()

# Initialize aiohttp app
app = web.Application(middlewares=[db])
db.init_app(app, dict(dsn=PG_URL))


# Definition of table
class User(db.Model):
    __tablename__ = "simple_aiohttp_demo_users"

    id = db.Column(db.BigInteger(), primary_key=True)
    nickname = db.Column(db.Unicode(), default="unnamed")


# Definition of routes
routes = web.RouteTableDef()


@routes.get("/")
async def index(request):
    return web.Response(text="Hello, world!")


@routes.get("/users/{uid}")
async def get_user(request):
    uid = int(request.match_info["uid"])
    q = User.query.where(User.id == uid)
    return web.json_response((await q.gino.first_or_404()).to_dict())


@routes.post("/users")
async def add_user(request):
    form = await request.json()
    u = await User.create(nickname=form.get("name"))
    return web.json_response(u.to_dict())


app.router.add_routes(routes)


async def create(app_):
    await db.gino.create_all()


app.on_startup.append(create)

if __name__ == "__main__":
    web.run_app(
        app,
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", "5000")),
    )

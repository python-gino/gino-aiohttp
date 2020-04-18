from aiohttp import web

from ..models.users import db, User

routes = web.RouteTableDef()


@routes.get("/users/{uid}")
async def get_user(request):
    q = User.query.where(User.id == int(request.match_info["uid"]))
    return web.json_response((await q.gino.first_or_404()).to_dict())


@routes.post("/users")
async def add_user(request):
    user = await request.json()
    u = await User.create(nickname=user["name"])
    return web.json_response(u.to_dict())


def init_app(app):
    app.router.add_routes(routes)

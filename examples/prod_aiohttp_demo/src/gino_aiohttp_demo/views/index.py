from aiohttp import web

routes = web.RouteTableDef()


@routes.get("/")
async def index(request):
    return web.json_response({"message": "Hello, world!"})


def init_app(app):
    app.router.add_routes(routes)

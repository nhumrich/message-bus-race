import message
import asyncio
from aiohttp import web
from nats.aio.client import Client as NATS

nc = NATS()

async def handle(request):
    reply_message = message.get_message()
    response = {'message': reply_message}
    return web.json_response(response)

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', handle)
    handler = app.make_handler()
    srv = await loop.create_server(handler, '0.0.0.0', 8886)
    print('======= Server running at :8886 =======')
    return app, srv, handler

if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(run(loop))
    # loop.close()
    loop = asyncio.get_event_loop()
    app, srv, handler = loop.run_until_complete(init(loop))
    loop.run_forever()

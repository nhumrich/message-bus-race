import asyncio
import aiohttp
from aiohttp import web
from nats.aio.client import Client as NATS

nc = NATS()
loop = asyncio.get_event_loop()

async def handle(request):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://127.0.0.1:8886') as resp:
            print(await resp.text())
            return web.json_response({'message': await resp.text()})

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', handle)
    handler = app.make_handler()
    srv = await loop.create_server(handler, '0.0.0.0', 8887)
    print('======= Server running at :8887 =======')
    return app, srv, handler

if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(run(loop))
    # loop.close()
    app, srv, handler = loop.run_until_complete(init(loop))
    loop.run_forever()

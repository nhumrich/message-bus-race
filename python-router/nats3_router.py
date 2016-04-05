import asyncio
from aiohttp import web
from nats.aio.client import Client as NATS

nc = NATS()

async def handle(request):
    msg = await nc.timed_request('test', 'foo'.encode(), timeout=10)
    response = b'{"message": "' + msg.data + b'"}'
    print('got msg, size={}'.format(msg.data.__sizeof__()))
    return web.json_response(body=response)

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', handle)
    handler = app.make_handler()
    srv = await loop.create_server(handler, '0.0.0.0', 8888)
    print('======= Server running at :8888 =======')
    return app, srv, handler

async def init_nats(loop):
    options = {
        'servers': ['nats://localhost:4222'],
        'io_loop': loop,
    }

    await nc.connect(**options)
    print('Connected to NATS at {}...'.format(nc.connected_url.netloc))

    async def subscribe_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))
        await nc.publish(reply, 'here ya go'.encode())

    # await nc.subscribe('test', cb=subscribe_handler)

if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(run(loop))
    # loop.close()
    loop = asyncio.get_event_loop()
    app, srv, handler = loop.run_until_complete(init(loop))
    loop.run_until_complete(init_nats(loop))
    loop.run_forever()

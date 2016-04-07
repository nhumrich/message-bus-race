import asyncio
import aiohttp
import aioamqp
import uuid
import os
from aiohttp import web
from nats.aio.client import Client as NATS

nc = NATS()
NATS_SERVER = 'nats://' + os.getenv('NATS_SERVER', 'localhost') + ':4222'
RABBIT_SERVER = os.getenv('RABBIT_SERVER', 'localhost')
HTTP_SERVER = 'http://' + os.getenv('HTTP_SERVER', '127.0.0.1:8888')

transport = None
protocol = None
channel = None


async def handle_rabbit(request):
    d = {'response': None}
    rid = await channel.queue_declare(queue_name='', exclusive=True)
    callback_queue = rid['queue']
    waiter = asyncio.Event()
    corr_id = str(uuid.uuid4())
    response = None

    async def on_response(channel, body, envelope, properties):
        if corr_id == properties.correlation_id:
            d['response'] = body

        waiter.set()

    await channel.basic_consume(on_response, no_ack=True, queue_name=callback_queue)

    await channel.basic_publish(
        payload='foo'.encode(),
        exchange_name='',
        routing_key='test',
        properties={
            'reply_to': callback_queue,
            'correlation_id': corr_id,
        },
    )

    await waiter.wait()

    msg = d['response']
    r = b'{"message": "' + msg + b'"}'
    # print('got msg, size={}'.format(r.__sizeof__()))
    return web.json_response(body=r)


async def handle_nats(request):
    msg = await nc.timed_request('test', 'foo'.encode(), timeout=10)
    response = b'{"message": "' + msg.data + b'"}'
    # print('got msg, size={}'.format(msg.data.__sizeof__()))
    return web.json_response(body=response)


async def handle_http(request):
    async with aiohttp.ClientSession() as session:
        async with session.post(HTTP_SERVER, data='foo'.encode()) as resp:
            # print(await resp.text())
            return web.json_response({'message': await resp.text()})


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/http', handle_http)
    app.router.add_route('GET', '/nats', handle_nats)
    app.router.add_route('GET', '/rabbit', handle_rabbit)
    handler = app.make_handler()
    srv = await loop.create_server(handler, '0.0.0.0', 8080)
    print('======= Server running at :8080 =======')
    return app, srv, handler


async def init_nats(loop):
    options = {
        'servers': [NATS_SERVER],
        'io_loop': loop,
    }

    await nc.connect(**options)
    print('Connected to NATS at {}...'.format(nc.connected_url.netloc))


async def init_rabbit():
    global transport, protocol, channel
    transport, protocol = await aioamqp.connect(host=RABBIT_SERVER)

    channel = await protocol.channel()
    await channel.queue_declare(queue_name='test')
    await channel.basic_qos(prefetch_count=1, prefetch_size=0, connection_global=False)


if __name__ == '__main__':
    # setup
    loop = asyncio.get_event_loop()
    app, srv, handler = loop.run_until_complete(init(loop))
    loop.run_until_complete(init_nats(loop))
    loop.run_until_complete(init_rabbit())

    # Run server
    loop.run_forever()

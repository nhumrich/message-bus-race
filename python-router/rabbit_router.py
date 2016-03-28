import asyncio
from aiohttp import web
import aioamqp
import uuid
import json

transport = None
protocol = None
channel = None

async def handle(request):
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
        payload='foobar',
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
    print('got msg, size={}'.format(r.__sizeof__()))
    return web.json_response(body=r)


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', handle)
    handler = app.make_handler()
    srv = await loop.create_server(handler, '0.0.0.0', 8881)
    print('======= Server running at :8888 =======')
    return app, srv, handler


async def init_rabbit():
    global transport, protocol, channel
    transport, protocol = await aioamqp.connect()

    channel = await protocol.channel()
    await channel.queue_declare(queue_name='test')
    await channel.basic_qos(prefetch_count=1, prefetch_size=0, connection_global=False)

    async def on_request(channel, body, envelope, properties):
        print('got request')
        await channel.basic_publish(payload='responding for you',
                                    exchange_name='',
                                    routing_key=properties.reply_to,
                                    properties={'correlation_id': properties.correlation_id})
        await channel.basic_client_ack(delivery_tag=envelope.delivery_tag)

    # await channel.basic_consume(on_request, queue_name='test')
    # print('awaiting Messages')

if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(run(loop))
    # loop.close()
    loop = asyncio.get_event_loop()
    app, srv, handler = loop.run_until_complete(init(loop))
    loop.run_until_complete(init_rabbit())
    loop.run_forever()

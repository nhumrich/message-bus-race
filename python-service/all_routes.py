import asyncio
import aioamqp
from aiohttp import web
import os
from nats.aio.client import Client as NATS
import message

nc = NATS()
NATS_SERVER = 'nats://' + os.getenv('NATS_SERVER', 'localhost') + ':4222'
RABBIT_SERVER = os.getenv('RABBIT_SERVER', 'localhost')


async def handle_http(request):
    reply_message = message.get_message()
    response = {'message': reply_message}
    return web.json_response(response)


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('POST', '/', handle_http)
    handler = app.make_handler()
    srv = await loop.create_server(handler, '0.0.0.0', 8888)
    print('======= Server running at :8888 =======')
    return app, srv, handler


async def init_nats(loop):
    options = {
        'servers': [NATS_SERVER],
        'io_loop': loop,
    }

    await nc.connect(**options)
    print('Connected to NATS at {}...'.format(nc.connected_url.netloc))

    async def subscribe_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        # print("Received a message on '{subject} {reply}': {data}".format(
        #     subject=subject, reply=reply, data=data))
        reply_message = message.get_message()
        await nc.publish(reply, reply_message.encode())

    await nc.subscribe('test', cb=subscribe_handler)


async def init_rabbit():
    transport, protocol = await aioamqp.connect(host=RABBIT_SERVER)

    channel = await protocol.channel()
    await channel.queue_declare(queue_name='test')
    await channel.basic_qos(prefetch_count=1, prefetch_size=0, connection_global=False)

    async def on_request(channel, body, envelope, properties):
        reply_message = message.get_message()
        await channel.basic_publish(payload=reply_message.encode(),
                                    exchange_name='',
                                    routing_key=properties.reply_to,
                                    properties={'correlation_id': properties.correlation_id})
        await channel.basic_client_ack(delivery_tag=envelope.delivery_tag)

    await channel.basic_consume(on_request, queue_name='test')
    print('awaiting rabbit Messages')


if __name__ == '__main__':
    # setup
    loop = asyncio.get_event_loop()
    app, srv, handler = loop.run_until_complete(init(loop))
    loop.run_until_complete(init_nats(loop))
    loop.run_until_complete(init_rabbit())

    # run server
    loop.run_forever()

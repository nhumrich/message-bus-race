import asyncio
from aiohttp import web
import aioamqp
import message


async def init_rabbit():
    transport, protocol = await aioamqp.connect()

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
    print('awaiting Messages')

if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(run(loop))
    # loop.close()
    loop = asyncio.get_event_loop()
    # app, srv, handler = loop.run_until_complete(init(loop))
    loop.run_until_complete(init_rabbit())
    loop.run_forever()

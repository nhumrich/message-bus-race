import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers
import message

nc = NATS()


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
        reply_message = message.get_message()
        await nc.publish(reply, reply_message.encode())

    await nc.subscribe('test', cb=subscribe_handler)
    nc.subscribe()

if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(run(loop))
    # loop.close()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_nats(loop))
    loop.run_forever()

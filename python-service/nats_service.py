import tornado.ioloop
import tornado.web
import tornado.gen
import time
from nats.io.client import Client as NATS
import message

nc = NATS()


class Nats():

    @tornado.gen.coroutine
    def connect(self):
        options = { "verbose": True, "servers": ["nats://127.0.0.1:4222"] }
        yield nc.connect(**options)

        def test(msg):
            reply_message = message.get_message()
            request_message = msg.data # Read data just to say we did
            nc.publish(msg.reply, reply_message)

        yield nc.subscribe('test', '', test)


if __name__ == "__main__":
    nats = Nats()
    loop = tornado.ioloop.IOLoop.instance()
    loop.add_timeout(time.time() + 1, nats.connect)
    tornado.ioloop.IOLoop.current().start()

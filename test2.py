import tornado.ioloop
import tornado.web
import tornado.gen
import time
from nats_service.io.client import Client as NATS


nc = NATS()


class NatsHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def _send_request(self, msg):
        self.write({"message": msg})
        self.finish()

    @tornado.web.asynchronous
    def get(self):
        def get_response(msg):
            print('got msg {}'.format(msg.data))
            self._send_request(msg.data)

        nc.request('test', 'foo', cb=get_response)


def make_app():
    return tornado.web.Application([
        (r"/nats", NatsHandler),
    ])


class Nats():

    @tornado.gen.coroutine
    def connect(self):
        options = { "verbose": True, "servers": ["nats://127.0.0.1:4222"] }
        yield nc.connect(**options)

        def test(msg):
            print('this is a test {}'.format(msg))
            nc.publish(msg.reply, msg.data + 'bar')

        yield nc.subscribe('test', '', test)


if __name__ == "__main__":
    nats = Nats()
    app = make_app()
    app.listen(8888)
    loop = tornado.ioloop.IOLoop.instance()
    loop.add_timeout(time.time() + 1, nats.connect)
    tornado.ioloop.IOLoop.current().start()

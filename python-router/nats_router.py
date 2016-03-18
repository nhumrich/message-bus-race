import tornado.ioloop
import tornado.web
import tornado.gen
import time
from nats.io.client import Client as NATS


nc = NATS()


class MainHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def _send_request(self, msg):
        self.write({"message": msg})
        self.finish()

    @tornado.web.asynchronous
    def get(self):
        def get_response(msg):
            print('got msg, size={}'.format(msg.data.__sizeof__()))
            self._send_request(msg.data)

        nc.request('test', 'foo', cb=get_response)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


class Nats():

    @tornado.gen.coroutine
    def connect(self):
        options = {"verbose": True, "servers": ["nats://127.0.0.1:4222"]}
        yield nc.connect(**options)

if __name__ == "__main__":
    nats = Nats()
    app = make_app()
    app.listen(8888)
    loop = tornado.ioloop.IOLoop.instance()
    loop.add_timeout(time.time() + 1, nats.connect)
    tornado.ioloop.IOLoop.current().start()
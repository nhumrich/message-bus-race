import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.httpclient
import message


class MainHandler(tornado.web.RequestHandler):
    client = tornado.httpclient.AsyncHTTPClient()

    def data_received(self, chunk):
        pass

    def _send_request(self, msg):
        print(msg)
        self.write(msg)
        self.finish()

    @tornado.web.asynchronous
    def get(self):
        reply_message = message.get_message()
        self._send_request(reply_message)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8886)
    tornado.ioloop.IOLoop.current().start()

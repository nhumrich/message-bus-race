import tornado.ioloop
import tornado.web
import tornado.gen
import tornado.httpclient


class MainHandler(tornado.web.RequestHandler):
    client = tornado.httpclient.AsyncHTTPClient()

    def data_received(self, chunk):
        pass

    def _send_request(self, msg):
        print(msg)
        self.write({"message": msg.body})
        self.finish()

    @tornado.web.asynchronous
    def get(self):
        def get_response(response):
            self._send_request(response)

        self.client.fetch('http://127.0.0.1:8886', get_response)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8887)
    tornado.ioloop.IOLoop.current().start()

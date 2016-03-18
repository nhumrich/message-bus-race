from bottle import route, run, response
import json
from nats_service.client import NatsClient
import time
import sys



@route('/rabbit')
def rabbitmq():
    return json.dumps({'text': 'foobar'})


@route('/nats')
def nats():
    return json.dumps({'text': 'foobar'})


@route('/crossbar')
def crossbario():
    return json.dumps({'text': 'foobar'})


NATS_URI = "nats://nats:nats@127.0.0.1:4222"


def main():
    try:
        nats = NatsClient(uris=NATS_URI)
        nats.start()
        time.sleep(1)

        def subscribe_blk(msg, reply):
            print(msg)
            nats.publish(reply, msg + 'foo')

        sid = nats.subscribe("job", subscribe_blk)
        run(host='0.0.0.0', port=8001)
    except KeyboardInterrupt as ex:
        print("ByeBye.")
        sys.exit(0)

if __name__ == '__main__':
    main()
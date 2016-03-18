from bottle import route, run, response
import json
from nats_router.client import NatsClient

import time
import sys

# Setup

nats = None

@route('/rabbit')
def rabbitmq():
    return json.dumps({'text': 'foobar'})


def nats_callback(msg):
    print(msg)
    print('hello')
    return msg + 'bar'


@route('/nats')
def nats():
    rep = nats.request("job", "Add to me: ", nats_callback)
    print(nats.stat.query())
    return json.dumps({'text': rep})


@route('/crossbar')
def crossbario():
    return json.dumps({'text': 'foobar'})

NATS_URI = "nats://nats:nats@127.0.0.1:4222"


def main():
    global nats
    try:
        nats = NatsClient(uris=NATS_URI)
        nats.start()
        time.sleep(1)

        def subscribe_blk(msg, reply):
            print("[PUB]: {}".format(msg))
            nats.publish(reply, "I can do this job.")

        # sid = nats.subscribe("job", subscribe_blk)
        run(host='0.0.0.0', port=8000)
    except KeyboardInterrupt as ex:
        print("ByeBye.")
        sys.exit(0)

if __name__ == '__main__':
    main()
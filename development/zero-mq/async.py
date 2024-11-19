import asyncio
import datetime
from functools import partial

import zmq
import zmq.asyncio
from development_producer import message_printer, random_int_producer
from make_market.producer_consumer.zero_mq import PubSubWithZeroMQ

context = zmq.asyncio.Context()


FRONTEND_ADDR = "inproc://frontend"
BACKEND_ADDR = "inproc://backend"

async def run_server(host, port):
    socket = context.socket(zmq.PUB)
    socket.bind(FRONTEND_ADDR)

    while 1:
        await asyncio.sleep(0.1)

        print('publish')
        await socket.send_multipart([b'topic\0', str(datetime.datetime.now()).encode()])


def run_proxy():
    subscriber = context.socket(zmq.XSUB)
    subscriber.connect(FRONTEND_ADDR)

    publisher = context.socket(zmq.XPUB)
    publisher.bind(BACKEND_ADDR)

    zmq.proxy(subscriber, publisher)

async def run_client():
    socket = context.socket(zmq.SUB)
    # We can connect to several endpoints if we desire, and receive from all.
    socket.connect(BACKEND_ADDR)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    while 1:
        print(await socket.recv())


async def main():

    pubsub = PubSubWithZeroMQ()


    # this is also valid:
    await asyncio.gather(
            pubsub.start_publishers(publishers=[random_int_producer]),
            pubsub.start_subscribers(subscribers=[partial(message_printer, id=i) for i in range(3)]),
            pubsub.setup_proxy(),
            run_client(),
            run_client(),
        # run_server('127.0.0.1', 2000)
    )

if __name__ == '__main__':
    asyncio.run(main())

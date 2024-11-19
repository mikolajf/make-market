# Espresso Pattern
# This shows how to capture data using a pub-sub proxy
#

import asyncio
import binascii
import datetime
import os
import time
from random import randint
from string import ascii_uppercase as uppercase
from threading import Thread

import zmq
import zmq.asyncio
from zmq.devices import monitored_queue


def zpipe(ctx):
    """build inproc pipe for talking to threads

    mimic pipe used in czmq zthread_fork.

    Returns a pair of PAIRs connected via inproc
    """
    a = ctx.socket(zmq.PAIR)
    b = ctx.socket(zmq.PAIR)
    a.linger = b.linger = 0
    a.hwm = b.hwm = 1
    iface = "inproc://%s" % binascii.hexlify(os.urandom(8))
    a.bind(iface)
    b.connect(iface)
    return a,b


# The subscriber thread requests messages starting with
# A and B, then reads and counts incoming messages.

def subscriber_thread():
    ctx = zmq.Context.instance()

    # Subscribe to "A" and "B"
    subscriber = ctx.socket(zmq.SUB)
    subscriber.connect("tcp://localhost:6001")
    # subscriber.setsockopt(zmq.SUBSCRIBE, b"A")
    # subscriber.setsockopt(zmq.SUBSCRIBE, b"B")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

    while True:
        try:
            msg = subscriber.recv_multipart()
            print(f"Received: {msg}")
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break           # Interrupted
            else:
                raise

    print("Subscriber received %d messages" % count)


# publisher thread
# The publisher sends random messages starting with A-J:

def publisher_thread():
    ctx = zmq.Context.instance()

    publisher = ctx.socket(zmq.PUB)
    publisher.bind("tcp://*:6000")

    while True:
        string = "%s-%05d" % (uppercase[randint(0,10)], randint(0,100000))
        try:
            publisher.send(string.encode('utf-8'))
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break           # Interrupted
            else:
                raise
        time.sleep(0.1)         # Wait for 1/10th second


async def async_publisher():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:6000")

    while 1:
        await asyncio.sleep(0.1)
        print('publish')
        await socket.send(str(datetime.datetime.now()).encode())


# listener thread
# The listener receives all messages flowing through the proxy, on its
# pipe. Here, the pipe is a pair of ZMQ_PAIR sockets that connects
# attached child threads via inproc. In other languages your mileage may vary:

def listener_thread(pipe):

    # Print everything that arrives on pipe
    while True:
        try:
            print(pipe.recv_multipart())
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break           # Interrupted


# main thread
# The main task starts the subscriber and publisher, and then sets
# itself up as a listening proxy. The listener runs as a child thread:

def main():

    # Start child threads
    ctx = zmq.Context.instance()
    s_thread = Thread(target=subscriber_thread)
    s_thread.start()

    # p_thread = Thread(target=publisher_thread)
    # p_thread.start()

    def async_entrypoint():
        asyncio.run(async_publisher())

    async_thread = Thread(target=async_entrypoint)
    async_thread.start()

    # pipe = zpipe(ctx)

    subscriber = ctx.socket(zmq.XSUB)
    subscriber.connect("tcp://localhost:6000")

    publisher = ctx.socket(zmq.XPUB)
    publisher.bind("tcp://*:6001")

    # l_thread = Thread(target=listener_thread, args=(pipe[1],))
    # l_thread.start()



    try:
        # monitored_queue(subscriber, publisher, pipe[0], b'pub', b'sub')
        zmq.proxy(subscriber, publisher)

    except KeyboardInterrupt:
        print("Interrupted")

    del subscriber, publisher, pipe
    ctx.term()

if __name__ == '__main__':
    main()

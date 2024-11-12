import time
from random import randint
from string import ascii_uppercase as uppercase
from threading import Thread

import zmq

FRONTEND_ADDR = "inproc://frontend"
BACKEND_ADDR = "inproc://backend"

# Publisher thread
def publisher_thread():
    ctx = zmq.Context.instance()
    publisher = ctx.socket(zmq.PUB)
    publisher.bind(FRONTEND_ADDR)

    while True:
        string = "%s-%05d" % (uppercase[randint(0, 9)], randint(0, 100000))
        try:
            publisher.send(string.encode('utf-8'))
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break  # Interrupted
            else:
                raise
        time.sleep(0.1)  # Wait for 1/10th second

# Subscriber thread
def subscriber_thread(subscriber_id):
    ctx = zmq.Context.instance()
    subscriber = ctx.socket(zmq.SUB)
    subscriber.connect(BACKEND_ADDR)
    subscriber.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        try:
            message = subscriber.recv_string()
            print(f"Subscriber {subscriber_id} received: {message}")
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break  # Interrupted


# Main function
def main():
    ctx = zmq.Context.instance()

    # Start publisher and subscriber threads
    p_thread = Thread(target=publisher_thread)
    p_thread.start()

    # Start three subscriber threads
    for i in range(3):
        s_thread = Thread(target=subscriber_thread, args=(i,))
        s_thread.start()

    # Setup XSUB and XPUB sockets
    subscriber = ctx.socket(zmq.XSUB)
    subscriber.connect(FRONTEND_ADDR)

    publisher = ctx.socket(zmq.XPUB)
    publisher.bind(BACKEND_ADDR)

    try:
        zmq.proxy(subscriber, publisher)
    except KeyboardInterrupt:
        print("Interrupted")

    del subscriber, publisher
    ctx.term()

if __name__ == '__main__':
    main()

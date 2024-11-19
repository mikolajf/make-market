import asyncio
import threading
import time
from typing import NoReturn
import zmq
import zmq.asyncio

from make_market.producer_consumer.zero_mq import PubSubWithZeroMQ


async def standalone_publisher(address: str) -> NoReturn:
    context = zmq.asyncio.Context.instance()
    socket = context.socket(zmq.PUB)
    socket.bind(address)
    
    while True:
        await asyncio.sleep(1)
        message = "Hello"
        print(f"Publishing: {message}")
        await socket.send_string(message)

async def publisher(socket: zmq.asyncio.Socket) -> NoReturn:
    
    while True:
        await asyncio.sleep(1)
        message = "Hello"
        print(f"Publishing: {message}")
        await socket.send_string(message)


def threaded_publisher(socket: zmq.Socket) -> NoReturn:
    
    while True:
        time.sleep(1)
        message = "Hello"
        print(f"Publishing: {message}")
        socket.send_string(message)

def subscriber(socket: zmq.Socket, id: int) -> NoReturn:
    
    while True:
        message = socket.recv_string()
        print(f"Subscriber {id} received: {message}")


async def async_subscriber(socket: zmq.asyncio.Socket):

    while 1:
        msg = await socket.recv_string()
        print(f"Async Subscriber received: {msg}")

def main():
    print('Hello, World!')

    ps = PubSubWithZeroMQ(in_address="tcp://localhost:5555", out_address="tcp://localhost:5556")
    ps.start()

    sub_thread1 = threading.Thread(target=subscriber, args=(ps.subscriber_socket,1))
    sub_thread2 = threading.Thread(target=subscriber, args=(ps.subscriber_socket,2))
    # pub_thread = threading.Thread(target=threaded_publisher, args=(ps.publisher_socket,))
    # pub_thread = threading.Thread(target=lambda: asyncio.run(standalone_publisher(ps.FRONTEND_ADDR)))


    sub_thread1.start()
    sub_thread2.start()
    # pub_thread.start()


    # asyncio.run(publisher(ps.async_publisher_socket))

    async def async_entrypoint():
        await asyncio.gather(
            publisher(ps.async_publisher_socket),
            async_subscriber(ps.async_subscriber_socket)   
        )

    asyncio.run(async_entrypoint())


if __name__ == '__main__':
    main()
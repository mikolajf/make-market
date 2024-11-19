import asyncio
import threading
import time

import pytest
import zmq
import zmq.asyncio
from make_market.producer_consumer.zero_mq import PubSubWithZeroMQ

received = False


async def async_publisher(socket: zmq.asyncio.Socket) -> None:
    for _ in range(2):
        await asyncio.sleep(1)
        await socket.send(b"123")


def threaded_publisher(socket: zmq.Socket[bytes]) -> None:
    for _ in range(2):
        time.sleep(1)
        socket.send(b"123")


def subscriber(socket: zmq.Socket[bytes]) -> bytes:
    return socket.recv()


async def async_subscriber(socket: zmq.asyncio.Socket) -> None:
    global received  # noqa: PLW0603
    while not received:
        await socket.recv()
        received = True


@pytest.fixture
async def zmq_middleware():
    ps = PubSubWithZeroMQ(
        in_address="tcp://localhost:5555", out_address="tcp://localhost:5556"
    )
    ps.start()
    yield ps
    ps.stop()


@pytest.mark.asyncio
async def test_async_publisher(zmq_middleware: PubSubWithZeroMQ) -> None:
    await async_publisher(zmq_middleware.async_publisher_socket)


def test_threaded_publisher(zmq_middleware: PubSubWithZeroMQ) -> None:
    pub_thread = threading.Thread(
        target=threaded_publisher, args=(zmq_middleware.publisher_socket,)
    )
    pub_thread.start()

    try:
        message: bytes = zmq_middleware.subscriber_socket.recv()
        assert message == b"123"
    finally:
        pub_thread.join()


@pytest.mark.asyncio
async def test_async_subscriber(zmq_middleware: PubSubWithZeroMQ) -> None:
    pub_socket = zmq_middleware.async_publisher_socket
    sub_socket = zmq_middleware.async_subscriber_socket

    await asyncio.gather(async_publisher(pub_socket), async_subscriber(sub_socket))

    assert received


def test_subscriber(zmq_middleware: PubSubWithZeroMQ) -> None:
    pub_socket = zmq_middleware.publisher_socket
    sub_socket = zmq_middleware.subscriber_socket

    pub_thread = threading.Thread(target=threaded_publisher, args=(pub_socket,))
    pub_thread.start()

    try:
        message = subscriber(sub_socket)
        assert message == b"123"
    finally:
        pub_thread.join()

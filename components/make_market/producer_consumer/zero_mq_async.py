# Publisher thread
import asyncio
from collections.abc import Callable
from typing import Final

import zmq
import zmq.asyncio
from make_market.log.core import get_logger

PUBLISHER_THROTTHLE: Final[float] = 0.1

FRONTEND_ADDR = "inproc://frontend"
BACKEND_ADDR = "inproc://backend"


logger = get_logger(__name__)


async def publish_messages(data_generator: Callable[[], bytes]) -> None:
    """
    Publishes messages generated by the provided data generator function to a ZeroMQ PUB socket.

    Args:
        data_generator (Callable[[], bytes]): A callable that returns a bytes object representing the data to be published.

    Raises:
        zmq.ZMQError: If an error occurs with the ZeroMQ socket, other than an interruption (zmq.ETERM).

    Notes:
        The function runs indefinitely, publishing messages at intervals of 0.1 seconds until interrupted.

    """
    ctx = zmq.asyncio.Context.instance()
    publisher = ctx.socket(zmq.PUB)
    publisher.bind(FRONTEND_ADDR)

    while True:
        try:
            data = await data_generator()
            await publisher.send(data)
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break  # Interrupted
            raise
        await asyncio.sleep(PUBLISHER_THROTTHLE)  # Wait for 1/10th second


# Subscriber thread
async def subscriber_thread(message_handler: Callable[[bytes], None]) -> None:
    """
    Starts a ZeroMQ subscriber thread that listens for messages and processes them using the provided message handler.

    Args:
        message_handler (Callable[[bytes], None]): A callback function that processes received messages.

    Raises:
        zmq.ZMQError: If there is an error with the ZeroMQ socket.

    """
    ctx = zmq.asyncio.Context().instance()
    subscriber = ctx.socket(zmq.SUB)
    subscriber.connect(BACKEND_ADDR)
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

    while True:
        try:
            message = await subscriber.recv()
            await message_handler(message)
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break  # Interrupted


class PubSubWithZeroMQ:
    """
    A class to handle publish-subscribe messaging using ZeroMQ.
    """

    def __init__(
        self,
        publishers: list[Callable[[], bytes]],
        subscribers: list[Callable[[bytes], None]],
        loop=None,
    ) -> None:
        self.ctx = zmq.asyncio.Context.instance()
        self.loop = loop if loop else asyncio.get_event_loop()
        self.subscribers = subscribers
        self.publishers = publishers
        self.closed = True

        self._awaits = []

    def start(self) -> None:
        """
        Sets up a ZeroMQ proxy for message forwarding between a subscriber and a publisher.

        This method creates a subscriber socket that connects to the frontend address and a publisher
        socket that binds to the backend address. It then starts the ZeroMQ proxy to forward messages
        between these sockets. If interrupted by a KeyboardInterrupt, it will print "Interrupted" and
        clean up the sockets and terminate the ZeroMQ context.

        Returns:
            None

        """
        subscriber = self.ctx.socket(zmq.XSUB)
        subscriber.connect(FRONTEND_ADDR)

        publisher = self.ctx.socket(zmq.XPUB)
        publisher.bind(BACKEND_ADDR)

        zmq.proxy(subscriber, publisher)

        for task in [self.publishers, self.subscribers]:
            self._awaits.append(task())

        del subscriber, publisher
        self.ctx.term()

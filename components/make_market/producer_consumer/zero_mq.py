# Publisher thread
from threading import Thread
from typing import Final

import zmq
import zmq.asyncio
from make_market.log.core import get_logger

PUBLISHER_THROTTHLE: Final[float] = 1


logger = get_logger(__name__)


class PubSubWithZeroMQ:
    """
    A class to handle publish-subscribe messaging using ZeroMQ.
    """

    FRONTEND_ADDR = "ipc://frontend"
    BACKEND_ADDR = "ipc://backend"

    def __init__(self) -> None:
        self.context = zmq.Context()
        self.async_context = zmq.asyncio.Context.instance()

    def start(self) -> None:
        """
        Starts the ZeroMQ proxy by setting it up.

        This method initializes and configures the ZeroMQ proxy by calling the
        `setup_proxy` method. It does not take any parameters and does not return
        any value.
        """
        self.setup_proxy()

    def stop(self) -> None:
        """
        Stops the ZeroMQ proxy by joining the proxy thread and destroying the contexts.

        This method ensures that the proxy thread is properly terminated and that
        the ZeroMQ contexts are cleaned up to release any resources held by them.
        """
        self.proxy_thread.join()
        self.context.destroy()
        self.async_context.destroy()

    def setup_proxy(self) -> None:
        """
        Sets up a ZeroMQ proxy with an interrupt handler.

        This method initializes two ZeroMQ sockets: one for incoming messages (XSUB)
        and one for outgoing messages (XPUB). It connects the incoming socket to the
        frontend address and binds the outgoing socket to the backend address.

        A separate thread is started to run the proxy with an interrupt handler that
        catches a KeyboardInterrupt and logs an interruption message.

        Raises:
            zmq.ZMQError: If there is an error in creating or binding the sockets.

        """
        in_proxy = self.context.socket(zmq.XSUB)
        in_proxy.connect(self.FRONTEND_ADDR)

        out_proxy = self.context.socket(zmq.XPUB)
        out_proxy.bind(self.BACKEND_ADDR)

        def _proxy_with_interrupt(
            in_proxy: zmq.Socket[bytes], out_proxy: zmq.Socket[bytes]
        ) -> None:
            try:
                zmq.proxy(in_proxy, out_proxy)
            except KeyboardInterrupt:
                logger.info("Interrupted")

        self.proxy_thread = Thread(
            target=_proxy_with_interrupt, args=(in_proxy, out_proxy)
        )
        self.proxy_thread.start()

    @property
    def async_publisher_socket(self) -> zmq.asyncio.Socket:
        """
        Creates and returns an asynchronous ZeroMQ publisher socket.

        This method initializes a PUB socket using the asynchronous context,
        binds it to the frontend address, and returns the socket.

        Returns:
            zmq.asyncio.Socket: The initialized and bound PUB socket.

        """
        publisher = self.async_context.socket(zmq.PUB)
        publisher.bind(self.FRONTEND_ADDR)

        return publisher

    @property
    def async_subscriber_socket(self) -> zmq.asyncio.Socket:
        """
        Creates and returns an asynchronous ZeroMQ subscriber socket.

        The socket is connected to the backend address specified by BACKEND_ADDR
        and subscribes to all messages.

        Returns:
            zmq.asyncio.Socket: An asynchronous ZeroMQ subscriber socket.

        """
        subscriber = self.async_context.socket(zmq.SUB)
        subscriber.connect(self.BACKEND_ADDR)
        subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        return subscriber

    @property
    def publisher_socket(self) -> zmq.Socket[bytes]:
        """
        Creates and returns a ZeroMQ publisher socket.

        This method initializes a ZeroMQ PUB socket, binds it to the frontend
        address specified by `self.FRONTEND_ADDR`, and returns the socket.

        Returns:
            zmq.Socket[bytes]: A ZeroMQ PUB socket bound to the frontend address.

        """
        publisher = self.context.socket(zmq.PUB)
        publisher.bind(self.FRONTEND_ADDR)

        return publisher

    @property
    def subscriber_socket(self) -> zmq.Socket[bytes]:
        """
        Creates and returns a ZeroMQ subscriber socket.

        The subscriber socket connects to the backend address specified by
        `self.BACKEND_ADDR` and subscribes to all messages.

        Returns:
            zmq.Socket[bytes]: A ZeroMQ subscriber socket.

        """
        subscriber = self.context.socket(zmq.SUB)
        subscriber.connect(self.BACKEND_ADDR)
        subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        return subscriber

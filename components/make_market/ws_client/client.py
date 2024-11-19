import asyncio
import json

import websockets
import zmq.asyncio
from make_market.dict_zip import dict_zip
from make_market.log.core import get_logger
from make_market.producer_consumer.protocols import ProducerProtocol, StartableStopable
from make_market.ws_server.requests_types import Actions, Request

logger = get_logger("ws_client")


class WebSocketConnectAsync(ProducerProtocol, StartableStopable):
    """
    WebSocketConnectAsync is a class that manages an asynchronous WebSocket connection
    and handles subscribing and unsubscribing to symbols based on a given configuration.

    # Attributes:
        url (str): The WebSocket URL to connect to.
        websocket (websockets.WebSocketClientProtocol | None): The WebSocket client protocol instance.
        config (dict): Configuration dictionary for symbol subscriptions.
        publisher_socket (zmq.asyncio.Socket): The ZeroMQ publisher socket for sending messages.

    Methods:
        __init__(url: str, config, publisher_socket: zmq.asyncio.Socket) -> None:
            Initializes the WebSocketConnectAsync instance with the given URL, configuration, and publisher socket.
        async _subscribe_to_new_symbol(symbol: str) -> None:
            Subscribes to a new symbol by sending a subscription request over the WebSocket.
        async _unsubscribe_from_symbol(symbol: str) -> None:
            Unsubscribes from a symbol by sending an unsubscription request over the WebSocket.
        async _send(message: str):
            Sends a message over the WebSocket connection.
        async _receive() -> dict:
            Receives a message from the WebSocket connection and returns it as a dictionary.
        async _send_receive(message: str) -> dict:
            Sends a message and waits for a response, returning the response as a dictionary.
        async connect() -> None:
            Connects to the WebSocket server and subscribes to symbols based on the initial configuration.
        async disconnect() -> None:
            Disconnects from the WebSocket server and closes the connection.
        async _main_loop():
            Main loop that continuously receives messages from the WebSocket and sends them to the publisher socket.
        async start():
            Starts the WebSocket connection and the main loop.
        async stop():
            Stops the WebSocket connection and the main loop.
        async on_config_change(config: dict) -> None:
            Handles configuration changes by subscribing or unsubscribing to symbols as needed.

    """

    def __init__(self, url: str, config, publisher_socket: zmq.asyncio.Socket) -> None:
        self.url = url
        self.websocket: websockets.WebSocketClientProtocol | None = None
        self.config = config  # dummy for now
        self.publisher_socket: zmq.asyncio.Socket = publisher_socket

    async def _subscribe_to_new_symbol(self, symbol: str) -> None:
        request = Request(action=Actions.SUBSCRIBE, symbol=symbol)
        response = await self._send(json.dumps(request))
        logger.info(f"Subscribed to {symbol}: {response}")

    async def _unsubscribe_from_symbol(self, symbol: str) -> None:
        request = Request(action=Actions.UNSUBSCRIBE, symbol=symbol)
        response = await self._send(json.dumps(request))
        logger.info(f"Unsubscribed from {symbol}: {response}")

    async def _send(self, message: str):
        if self.websocket is None:
            raise ConnectionError("WebSocket is not connected.")
        await self.websocket.send(message)

    async def _receive(self) -> dict:
        if self.websocket is None:
            raise ConnectionError("WebSocket is not connected.")
        response = await self.websocket.recv()
        return json.loads(response)

    async def _send_receive(self, message: str) -> dict:
        await self._send(message)
        return await self._receive()

    async def connect(self) -> None:
        """
        Asynchronously connects to the WebSocket server and subscribes to symbols based on the initial configuration.
        This method performs the following steps:
        1. Logs the attempt to connect to the WebSocket server.
        2. Establishes a WebSocket connection to the specified URL.
        3. Logs the successful connection.
        4. Logs the start of the subscription process for symbols.
        5. Iterates through the initial configuration and subscribes to each symbol if it is enabled.

        Raises:
            websockets.exceptions.InvalidURI: If the URL is invalid.
            websockets.exceptions.InvalidHandshake: If the handshake fails.
            websockets.exceptions.WebSocketException: For other WebSocket-related errors.

        """
        logger.info(f"Connecting to {self.url}")
        self.websocket = await websockets.connect(self.url)
        logger.info("Connected to WebSocket")

        logger.info("Subscribing to symbols based on initial config...")
        for symbols in self.config:
            if self.config[symbols]:
                await self._subscribe_to_new_symbol(symbols)

    async def disconnect(self) -> None:
        """
        Asynchronously disconnects the websocket connection if it is currently open.

        This method checks if the websocket attribute is not None, and if so, it closes the websocket connection
        and sets the websocket attribute to None.

        Returns:
            None

        """
        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None

    async def _main_loop(self):
        try:
            while True:
                response: dict = await self._receive()
                keys = "...".join(response.keys())
                await self.publisher_socket.send_string(keys)
        except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
            logger.info("KeyboardInterrupt, stopping client")
            await self.stop()

    async def start(self):
        """
        Asynchronously starts the WebSocket client by establishing a connection
        and then entering the main loop.
        This method first calls the `connect` method to establish a WebSocket
        connection. Once the connection is established, it logs the start of the
        main loop and then calls the `_main_loop` method to handle the main
        operations of the WebSocket client.

        Raises:
            Exception: If the connection or main loop encounters an error.

        """
        await self.connect()

        logger.info("Starting main loop")
        await self._main_loop()

    async def stop(self):
        """
        Asynchronously stops the client by disconnecting and logging the process.

        This method logs the stopping process, calls the `disconnect` method to
        disconnect the client, and logs once the client has stopped.

        Returns:
            None

        """
        logger.info("Stopping client")
        await self.disconnect()
        logger.info("Client stopped")

    async def on_config_change(self, config: dict) -> None:
        """
        Handle configuration changes for the WebSocket client.
        This method is called when there is a change in the configuration.
        It compares the new configuration with the current one and subscribes
        or unsubscribes from symbols accordingly.

        Args:
            config (dict): The new configuration dictionary.

        Returns:
            None

        """
        logger.info(f"Received config change: {config}")
        if self.config != config:
            for symbol, (old_config, new_config) in dict_zip(
                self.config, config
            ).items():
                if old_config and not new_config:
                    logger.info(f"Unsubscribing from {symbol}")
                    await self._unsubscribe_from_symbol(symbol)
                elif not old_config and new_config:
                    logger.info(f"Subscribing to {symbol}")
                    await self._subscribe_to_new_symbol(symbol)

            self.config = config

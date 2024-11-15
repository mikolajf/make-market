import asyncio
import json
from collections.abc import MutableMapping
from itertools import chain
from threading import Thread
from typing import TypeVar

import websockets
import zmq.asyncio
from make_market.log.core import get_logger
from make_market.producer_consumer.protocols import ProducerProtocol
from make_market.settings.models import Settings
from make_market.ws_client.threaded import ConfigurationService
from make_market.ws_server.requests_types import Actions, Request

logger = get_logger(__name__)


KT = TypeVar("KT")  # dict keys
VT = TypeVar("VT")  # dict values
DT = TypeVar("DT")  # dict default


def dict_zip(
    *dicts: MutableMapping[KT, VT], default: DT = None
) -> dict[KT, tuple[VT | DT, ...]]:
    """
    Zips multiple dictionaries into a single dictionary, combining values from each dictionary into tuples.

    Args:
        *dicts (MutableMapping[KT, VT]): Variable number of dictionaries to be zipped.
        default (DT, optional): Default value to use if a key is missing in any of the dictionaries. Defaults to None.

    Returns:
        dict[KT, tuple[VT | DT, ...]]: A dictionary where each key is present in at least one of the input dictionaries,
        and the value is a tuple containing values from each dictionary (or the default value if the key is missing).

    """
    output_dict = {}

    # iterating over all available keys (present in at least one dict)
    for key in set(chain(*dicts)):
        # getting value given key from each dictionary,
        # if missing, we use to "default" argument, e.g. None
        output_dict[key] = tuple(d.get(key, default) for d in dicts)

    return output_dict


class WebSocketConnectAsync(ProducerProtocol):
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
        self.websocket = await websockets.connect(self.url)

        for symbols in self.config:
            if self.config[symbols]:
                await self._subscribe_to_new_symbol(symbols)

    async def disconnect(self) -> None:
        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None

    async def start(self):
        await self.connect()

        try:
            while True:
                response: dict = await self._receive()
                print(len(response))
                await self.publisher_socket.send(b"Hello")
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt, stopping client")
            await self.stop()

    async def stop(self):
        await self.websocket.close()
        # self.thread.join()

    async def on_config_change(self, config: dict) -> None:
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


# The subscriber thread requests messages starting with
# A and B, then reads and counts incoming messages.


def subscriber_thread():
    ctx = zmq.Context.instance()

    # Subscribe to "A" and "B"
    subscriber = ctx.socket(zmq.SUB)
    subscriber.connect("tcp://localhost:6001")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

    while True:
        try:
            msg = subscriber.recv()
            print(f"Received: {msg}")
        except Exception as e:
            logger.error(e)
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                break  # Interrupted
            raise


if __name__ == "__main__":
    # Start child threads
    ctx = zmq.Context.instance()
    s_thread = Thread(target=subscriber_thread)
    s_thread.start()

    # proxy
    subscriber = ctx.socket(zmq.XSUB)
    subscriber.connect("tcp://localhost:6000")

    publisher = ctx.socket(zmq.XPUB)
    publisher.bind("tcp://*:6001")

    config_service = ConfigurationService()

    async_context = zmq.asyncio.Context()
    socket = async_context.socket(zmq.PUB)
    socket.bind("tcp://*:6000")

    # init client
    url = Settings().vendor_websocket.URL
    client = WebSocketConnectAsync(
        url, config=config_service.config, publisher_socket=socket
    )
    config_service.register_listener(client)

    async def start_client():
        await client.start()

        # proxy thread
        proxy_thread = Thread(target=zmq.proxy, args=(subscriber, publisher))
        proxy_thread.start()

    async def main():
        await asyncio.gather(
            client.start(), config_service.subscribe_to_config_changes()
        )

    asyncio.run(main())

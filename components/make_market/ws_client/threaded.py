import asyncio
import json
import time
from collections.abc import AsyncIterator, MutableMapping
from itertools import chain
from threading import Thread
from typing import Protocol, TypeVar

from make_market.producer_consumer.protocols import (
    ConfigListenerProtocol,
    ConfigurationServiceProtocol,
)
from make_market.settings.models import Settings
from make_market.ws_client import logger
from make_market.ws_server.requests_types import Actions, Request
from websockets.sync.client import ClientConnection, connect


class StartableStopable(Protocol):
    def start(self) -> None: ...

    def stop(self) -> None: ...


async def dummy_config_change_generator() -> AsyncIterator[dict[str, bool]]:
    """
    An asynchronous generator that yields configuration changes.

    This generator simulates configuration changes by yielding a dictionary
    with a key "active" and a boolean value. It waits for 1 second between
    each yield.

    Yields:
        dict: A dictionary with a single key "active" and a boolean value.

    """
    await asyncio.sleep(1)
    yield {"EUR/USD": True}
    await asyncio.sleep(1)
    yield {"JPY/USD": True, "EUR/USD": True}
    await asyncio.sleep(1)
    yield {}
    await asyncio.sleep(1)
    yield {"EUR/USD": True}


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


class ConfigurationService(ConfigurationServiceProtocol):
    def __init__(self, async_watch_function=dummy_config_change_generator):
        self.config = {"EUR/USD": True, "GBP/USD": True}
        self.async_watch_function = async_watch_function()
        self.listeners: list[ConfigListenerProtocol] = []

    def register_listener(self, listener: ConfigListenerProtocol) -> None:
        self.listeners.append(listener)


class WebSocketClient(StartableStopable):
    def __init__(self, url: str, config) -> None:
        self.url = url
        self.websocket: ClientConnection | None = None
        self.config = config  # dummy for now
        self.cache = {}

    def _subscribe_to_new_symbol(self, symbol: str) -> None:
        request = Request(action=Actions.SUBSCRIBE, symbol=symbol)
        response = self._send_receive(json.dumps(request))
        logger.info(f"Subscribed to {symbol}: {response}")

    def _unsubscribe_from_symbol(self, symbol: str) -> None:
        request = Request(action=Actions.UNSUBSCRIBE, symbol=symbol)
        response = self._send_receive(json.dumps(request))
        logger.info(f"Unsubscribed from {symbol}: {response}")

    def _send(self, message: str):
        if self.websocket is None:
            raise ConnectionError("WebSocket is not connected.")
        self.websocket.send(message)

    def _receive(self) -> dict:
        if self.websocket is None:
            raise ConnectionError("WebSocket is not connected.")
        response = self.websocket.recv()
        return json.loads(response)

    def _send_receive(self, message: str) -> dict:
        self._send(message)
        return self._receive()

    def connect(self) -> None:
        self.websocket = connect(self.url)

        for symbols in self.config:
            if self.config[symbols]:
                self._subscribe_to_new_symbol(symbols)

    def disconnect(self) -> None:
        if self.websocket is not None:
            self.websocket.close()
            self.websocket = None

    def producer(self):
        while True:
            response: dict = self._receive()
            timestamp = time.time()
            for key in response:
                self.cache[key] = timestamp
                yield response

    async def on_config_change(self, config: dict) -> None:
        logger.info(f"Received config change: {config}")
        if self.config != config:
            for symbol, (old_config, new_config) in dict_zip(
                self.config, config
            ).items():
                if old_config and not new_config:
                    logger.info(f"Unsubscribing from {symbol}")
                    self._unsubscribe_from_symbol(symbol)
                elif not old_config and new_config:
                    logger.info(f"Subscribing to {symbol}")
                    self._subscribe_to_new_symbol(symbol)

            self.config = config

    def start(self):
        self.connect()
        self.thread = Thread(target=self.producer)
        self.thread.start()

        try:
            while True:
                print(next(self.producer()))
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt, stopping client")
            client.stop()

    def stop(self):
        self.websocket.close()
        self.thread.join()


if __name__ == "__main__":
    config_service = ConfigurationService()

    shared_config = {"EUR/USD": True}

    url = Settings().vendor_websocket.URL
    client = WebSocketClient(url, config=config_service.config)

    config_service.register_listener(client)

    async def start_client():
        client.start()

    async def main():
        await asyncio.gather(
            client.start(), config_service.subscribe_to_config_changes()
        )

    asyncio.run(main())

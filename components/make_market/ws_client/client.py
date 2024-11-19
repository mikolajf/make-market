import json
from collections.abc import AsyncIterator

import websockets
from make_market.log.core import get_logger
from make_market.producer_consumer.protocols import ProducerProtocol
from make_market.ws_server.requests_types import Actions, Request

logger = get_logger(__name__)


class WebSocketConnect(ProducerProtocol):
    def __init__(self, url: str) -> None:
        self.url = url
        self.websocket: websockets.WebSocketClientProtocol | None = None
        self.config = {"EUR/USD": True}  # dummy for now

    async def connect(self) -> None:
        self.websocket = await websockets.connect(self.url)

        for symbols in self.config:
            if self.config[symbols]:
                await self._subscribe_to_new_symbol(symbols)

    async def disconnect(self) -> None:
        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None

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

    async def _subscribe_to_new_symbol(self, symbol: str) -> None:
        request = Request(action=Actions.SUBSCRIBE, symbol=symbol)
        response = await self._send_receive(json.dumps(request))

        logger.info(f"Subscribed to {symbol}: {response}")

    async def producer_generator(self) -> AsyncIterator[bytes]:
        while True:
            message = await self._receive()
            yield message

    async def on_config_change(self, config: dict) -> None:
        pass

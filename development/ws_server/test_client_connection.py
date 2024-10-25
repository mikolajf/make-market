import asyncio
import json
import uuid

import pytest
import pytest_asyncio
import websockets
from make_market.ws_server.core import Actions, Request, websocket_handler

# Test WebSocket server setup
WEBSOCKET_URL = "ws://localhost:8765"


@pytest_asyncio.fixture(scope="function")
async def run_server():
    async with websockets.serve(websocket_handler, "localhost", 8765):
        yield


# Helper class to simulate a WebSocket client
class WebSocketClient:
    def __init__(self, url: str):
        self.url = url
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.url)

    async def send(self, message: str):
        if self.websocket is None:
            raise ConnectionError("WebSocket is not connected.")
        await self.websocket.send(message)

    async def receive(self) -> dict:
        if self.websocket is None:
            raise ConnectionError("WebSocket is not connected.")
        response = await self.websocket.recv()
        return json.loads(response)

    async def send_receive(self, message: str) -> dict:
        await self.send(message)
        return await self.receive()

    async def close(self):
        if self.websocket is not None:
            await self.websocket.close()
            self.websocket = None


# Pytest fixture to provide a WebSocket client
@pytest_asyncio.fixture(scope="function")
async def websocket_client():
    client = WebSocketClient(WEBSOCKET_URL)
    await client.connect()
    yield client
    await client.close()


@pytest.mark.usefixtures("run_server")
@pytest.mark.asyncio
async def test_connection(websocket_client: WebSocketClient):
    # Send the message and receive the response
    request = Request(action=Actions.SUBSCRIBE, symbol="EUR/USD")
    response = await websocket_client.send_receive(json.dumps(request))

    # Verify that the new FX pair is in the response with the correct initial data
    assert response["message"] == "Subscribed to FX pair: EUR/USD"


@pytest.mark.usefixtures("run_server")
@pytest.mark.asyncio
async def test_price_updates(websocket_client: WebSocketClient):
    # Generate a unique symbol name
    symbol = f"EUR/USD-{uuid.uuid4()}"

    # Send the message and receive the response
    request = Request(action=Actions.SUBSCRIBE, symbol=symbol)
    initial_response = await websocket_client.send_receive(json.dumps(request))
    assert initial_response["message"] == f"Subscribed to FX pair: {symbol}"

    # Wait a moment for the server to update the price
    response = await websocket_client.receive()
    initial_price = response[symbol]["ask_prices"][0]

    # Wait a moment for the server to update the price
    await asyncio.sleep(1)

    # Send another message to receive updated prices
    response = await websocket_client.receive()

    # Check if the price has changed (within a reasonable range based on drift/volatility)
    updated_price = response[symbol]["ask_prices"][0]
    assert updated_price != initial_price


@pytest.mark.usefixtures("run_server")
@pytest.mark.asyncio
async def test_subscribe_unsubscribe(websocket_client: WebSocketClient):
    # Generate a unique symbol name
    symbol = f"EUR/USD-{uuid.uuid4()}"
    # Subscribe to the symbol
    request = Request(action=Actions.SUBSCRIBE, symbol=symbol)
    response = await websocket_client.send_receive(json.dumps(request))
    assert response["message"] == f"Subscribed to FX pair: {symbol}"

    # Unsubscribe from the symbol
    request = Request(action=Actions.UNSUBSCRIBE, symbol=symbol)
    new_response = await websocket_client.send_receive(json.dumps(request))
    assert new_response["message"] == f"Unsubscribed from FX pair: {symbol}"


@pytest.mark.usefixtures("run_server")
@pytest.mark.asyncio
async def test_subscribe_unsubscribe_resubscribe(websocket_client: WebSocketClient):
    # Generate a unique symbol name
    symbol1 = f"EUR/USD-{uuid.uuid4()}"
    symbol2 = f"GBP/USD-{uuid.uuid4()}"

    # Subscribe to the first symbol
    request1 = Request(action=Actions.SUBSCRIBE, symbol=symbol1)
    response1 = await websocket_client.send_receive(json.dumps(request1))
    assert response1["message"] == f"Subscribed to FX pair: {symbol1}"

    # Unsubscribe from the first symbol
    request_unsub1 = Request(action=Actions.UNSUBSCRIBE, symbol=symbol1)
    response_unsub1 = await websocket_client.send_receive(json.dumps(request_unsub1))
    assert response_unsub1["message"] == f"Unsubscribed from FX pair: {symbol1}"

    # Subscribe to the second symbol
    request2 = Request(action=Actions.SUBSCRIBE, symbol=symbol2)
    response2 = await websocket_client.send_receive(json.dumps(request2))
    assert response2["message"] == f"Subscribed to FX pair: {symbol2}"


@pytest.mark.usefixtures("run_server")
@pytest.mark.asyncio
async def test_multiple_subscriptions(websocket_client: WebSocketClient):
    # Subscribe to the first symbol
    request1 = Request(action=Actions.SUBSCRIBE, symbol="JPY/USD")
    response1 = await websocket_client.send_receive(json.dumps(request1))
    assert response1["message"] == "Subscribed to FX pair: JPY/USD"

    # Subscribe to the second symbol
    request2 = Request(action=Actions.SUBSCRIBE, symbol="GBP/USD")
    response2 = await websocket_client.send_receive(json.dumps(request2))
    assert response2["message"] == "Subscribed to FX pair: GBP/USD"

    # Wait a moment for the server to update the prices
    await asyncio.sleep(1)

    # Get the initial prices
    response = await websocket_client.receive()
    assert "JPY/USD" in response
    assert "GBP/USD" in response

    # Unsubscribe from the first symbol
    request_unsub = Request(action=Actions.UNSUBSCRIBE, symbol="JPY/USD")
    response_unsub = await websocket_client.send_receive(json.dumps(request_unsub))
    assert response_unsub["message"] == "Unsubscribed from FX pair: JPY/USD"

    # Wait a moment for the server to update the prices
    await asyncio.sleep(1)

    # Get the updated prices
    response = await websocket_client.receive()
    assert "JPY/USD" not in response
    assert "GBP/USD" in response

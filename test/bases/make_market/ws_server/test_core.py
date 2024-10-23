import asyncio
import json
import threading
import uuid

import pytest
import pytest_asyncio
import websockets

from make_market.ws_server.core import (
    Actions,
    Request,
    handler,
    run_webscoket_server,
)

# Test WebSocket server setup
WEBSOCKET_URL = "ws://localhost:8765"


@pytest_asyncio.fixture(autouse=True, scope="function")
async def run_server():
    async with websockets.serve(handler, "localhost", 8765):
        yield


# Helper function to simulate a WebSocket client
async def client_send_receive(message: str) -> dict:
    """
    Connect to the WebSocket server, send a message, and receive a response.

    :param message: Message to send to the server.
    :return: Parsed JSON response from the server.
    """
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        # Send message to WebSocket server
        await websocket.send(message)

        # Wait for the updated prices from the server
        response = await websocket.recv()
        return json.loads(response)


@pytest.mark.asyncio
async def test_connection():
    # Send the message and receive the response
    request = Request(action=Actions.SUBSCRIBE, symbol="EUR/USD")
    response = await client_send_receive(json.dumps(request))

    # Verify that the new FX pair is in the response with the correct initial data
    assert response["message"] == "Subscribed to FX pair: EUR/USD"


@pytest.mark.asyncio
async def test_price_updates():
    # Send the message and receive the response
    request = Request(action=Actions.SUBSCRIBE, symbol="EUR/USD")
    response = await client_send_receive(json.dumps(request))

    # Wait a moment for the server to update the price
    await asyncio.sleep(1)

    # Get the initial price
    initial_price = response["EUR/USD"]["ask_prices"][0]

    # Wait a moment for the server to update the price
    await asyncio.sleep(1)

    # Send another message to receive updated prices
    response = await client_send_receive("")

    # Check if the price has changed (within a reasonable range based on drift/volatility)
    updated_price = response["EUR/USD"]["ask_prices"][0]
    assert updated_price != initial_price


@pytest.mark.asyncio
async def test_subscribe_unsubscribe():
    # Generate a unique symbol name
    symbol = f"EUR/USD-{uuid.uuid4()}"
    # Subscribe to the symbol
    request = Request(action=Actions.SUBSCRIBE, symbol=symbol)
    response = await client_send_receive(json.dumps(request))
    assert response["message"] == f"Subscribed to FX pair: {symbol}"

    # Unsubscribe from the symbol
    request = Request(action=Actions.UNSUBSCRIBE, symbol=symbol)
    response = await client_send_receive(json.dumps(request))
    assert response["message"] == f"Unsubscribed from FX pair: {symbol}"

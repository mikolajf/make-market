import asyncio
import json

import pytest
import websockets

# Test WebSocket server setup
WEBSOCKET_URL = "ws://localhost:8765"


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


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_connection():
    # Send the message and receive the response
    response = await client_send_receive("Test message")

    # Verify that the new FX pair is in the response with the correct initial data
    assert "EUR/USD" in response
    assert isinstance(response["EUR/USD"]["price"], float)


@pytest.mark.xfail
@pytest.mark.asyncio
async def test_price_updates():
    # Send the message and receive the response
    response = await client_send_receive("Test message")

    # Get the initial price
    initial_price = response["EUR/USD"]["price"]

    # Wait a moment for the server to update the price
    await asyncio.sleep(1)

    # Send another message to receive updated prices
    response = await client_send_receive("Test message")

    # Check if the price has changed (within a reasonable range based on drift/volatility)
    updated_price = response["EUR/USD"]["price"]
    assert updated_price != initial_price
    assert (
        abs(updated_price - initial_price) <= 0.01
    )  # Allow small changes due to drift/volatility

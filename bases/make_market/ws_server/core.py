import asyncio
import json
import random
from typing import Dict, TypedDict

import websockets
from make_market.log.core import get_logger

# setup logger
logger = get_logger("ws_server")


# Define a type for FX pair data
class FXPairData(TypedDict):
    price: float
    drift: float
    volatility: float


# Dictionary to store FX pairs with their price, drift, and volatility
fx_pairs: Dict[str, FXPairData] = {}

# Simulated FX pairs and their base prices
fx_prices = {
    "EUR/USD": {
        "price": 0.8500,
        "drift": 0.0002,
        "volatility": 0.0005
    },
}


def get_updated_price(pair_data: FXPairData) -> float:
    """
    Simulate price update based on drift and volatility.

    :param pair_data: Dictionary containing price, drift, and volatility for an FX pair.
    :return: Updated FX pair price.
    """
    base_price: float = pair_data['price']
    drift: float = pair_data['drift']
    volatility: float = pair_data['volatility']

    # Simulate price drift and volatility (random fluctuation)
    drift_effect: float = drift * random.uniform(0.95, 1.05)  # Slight random factor to drift
    volatility_effect: float = random.uniform(-volatility, volatility)

    new_price: float = base_price + drift_effect + volatility_effect
    return round(new_price, 5)


def update_fx_prices() -> None:
    """
    Update prices for all FX pairs in the fx_pairs dictionary.
    """
    for pair, data in fx_prices.items():
        updated_price: float = get_updated_price(data)
        fx_prices[pair]['price'] = updated_price


async def fx_price_publisher(websocket: websockets.WebSocketServerProtocol, path: str) -> None:
    """
    WebSocket handler to publish FX prices and listen for new FX pairs.

    :param websocket: The WebSocket connection.
    :param path: The connection path.
    """
    logger.info(f"Client connected: {path}")

    # After receiving a new FX pair, update prices and send updates
    while True:
        if fx_prices:
            # Update FX prices
            update_fx_prices()
            logger.info(f"Updated prices: {fx_prices}")

            # Send updated prices to the client
            await websocket.send(json.dumps(fx_prices))

        # Wait for a second before the next update
        await asyncio.sleep(1)


async def main() -> None:
    """
    Main function to start the WebSocket server.
    """
    async with websockets.serve(fx_price_publisher, "localhost", 8765):
        logger.info("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())

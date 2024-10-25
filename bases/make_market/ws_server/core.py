import asyncio
import json
import random
from enum import StrEnum
from typing import TypedDict

import websockets
from make_market.log.core import get_logger
from make_market.orderbook.core import OrderBook

# setup logger
logger = get_logger("ws_server")


class Actions(StrEnum):
    """Enumeration for possible actions in the WebSocket server."""

    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


class Request(TypedDict):
    """
    Request is a TypedDict that represents the structure of a request in the system.

    Attributes:
        action (Actions): The action to be performed, represented by an instance of the Actions enum.
        symbol (str): The symbol associated with the request, typically representing a financial instrument.

    """

    action: Actions
    symbol: str


# Set to store FX symbols
subscriptions: set[str] = set()


async def consumer_handler(
    websocket: websockets.WebSocketServerProtocol,
) -> None:
    """Consumer handler, parses messages received from customers."""
    logger.debug("Consumer handler started.")
    try:
        async for message in websocket:
            try:
                logger.debug("Received message.")
                request: Request = json.loads(message)

                if "action" in request:
                    action = request["action"]
                    symbol = request.get("symbol")

                    if action == Actions.SUBSCRIBE and symbol:
                        if symbol not in subscriptions:
                            subscriptions.add(symbol)
                            msg = f"Subscribed to FX pair: {symbol}"

                        else:
                            msg = f"Already subscribed to FX pair: {symbol}"

                    elif action == Actions.UNSUBSCRIBE and symbol:
                        subscriptions.discard(symbol)
                        msg = f"Unsubscribed from FX pair: {symbol}"

                    else:
                        msg = "Invalid action or symbol."

                    await websocket.send(json.dumps({"message": msg}))
                    logger.info(msg)

            except json.JSONDecodeError:
                logger.info("Received invalid message, ignoring.")
    except websockets.exceptions.ConnectionClosed:
        # clear subscriptions when client disconnects
        subscriptions.clear()
        logger.info("Client disconnected inside consumer_handler.")


async def fx_price_publisher(
    websocket: websockets.WebSocketServerProtocol,
) -> None:
    """
    WebSocket handler to publish FX prices and listen for new FX pairs.

    :param websocket: The WebSocket connection.
    """
    while True:
        if subscriptions:
            message = {}
            for symbol in subscriptions:
                # get random midprice and spread
                m = random.uniform(1.0, 2.0)  # midprice  # noqa: S311
                s = random.uniform(0.01, 0.05)  # spread  # noqa: S311

                # create orderbook
                orderbook = OrderBook.random(midprice=m, spread=s)

                message[symbol] = orderbook.to_dict()

            try:
                # Send updated prices to the client
                await websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                # clear subscriptions when client disconnects
                subscriptions.clear()
                logger.info("Client disconnected inside fx_price_publisher.")
                break
        else:
            try:
                # Send heartbeat to the client
                await websocket.ensure_open()
            except websockets.exceptions.ConnectionClosed:
                logger.info("Client disconnected inside fx_price_publisher.")
                break

        # Wait for a second before the next update
        await asyncio.sleep(1)


async def websocket_handler(
    websocket: websockets.WebSocketServerProtocol,
) -> None:
    """
    Handles incoming WebSocket connections and concurrently runs the consumer handler
    and FX price publisher.

    Args:
        websocket (websockets.WebSocketServerProtocol): The WebSocket connection instance.

    Returns:
        None

    """
    await asyncio.gather(
        consumer_handler(websocket),
        fx_price_publisher(websocket),
    )


async def run_websocket_server(port: int = 8765) -> None:
    """
    Main function to start the WebSocket server.
    """
    async with websockets.serve(websocket_handler, "localhost", port):
        logger.info(f"WebSocket server started on ws://localhost:{port}")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(run_websocket_server())

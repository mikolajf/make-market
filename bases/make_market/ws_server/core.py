import asyncio
import json
from queue import Empty
import random
from enum import StrEnum
from typing import TypedDict

import websockets
from make_market.log.core import get_logger
from make_market.orderbook.core import OrderBook

# setup logger
logger = get_logger("ws_server")


class Actions(StrEnum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


class Request(TypedDict):
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
                logger.debug(f"Received message: {message}")
                request: Request = json.loads(message)

                if "action" in request:
                    action = request["action"]
                    symbol = request.get("symbol")

                    if action == Actions.SUBSCRIBE and symbol:
                        if symbol not in subscriptions:
                            subscriptions.add(symbol)
                            msg = f"Subscribed to FX pair: {symbol}"

                            # send message to the client
                            await websocket.send(json.dumps({"message": msg}))
                            logger.info(msg)

                        else:
                            msg = f"Already subscribed to FX pair: {symbol}"
                            # send message to the client
                            await websocket.send(json.dumps({"message": msg}))
                            logger.info(msg)

                    elif action == Actions.UNSUBSCRIBE and symbol:
                        subscriptions.discard(symbol)
                        logger.info(f"Unsubscribed from FX pair: {symbol}")

            except json.JSONDecodeError:
                logger.info("Received invalid message, ignoring.")
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected.")


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
                m = random.uniform(1.0, 2.0)  # midprice
                s = random.uniform(0.01, 0.05)  # spread

                # create orderbook
                orderbook = OrderBook.random(midprice=m, spread=s)

                message[symbol] = orderbook.to_dict()

            try:
                # Send updated prices to the client
                await websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                logger.info("Client disconnected.")
                break

        # Wait for a second before the next update
        await asyncio.sleep(1)


async def handler(websocket: websockets.WebSocketServerProtocol) -> None:
    await asyncio.gather(
        consumer_handler(websocket),
        fx_price_publisher(websocket),
    )


async def websocket_server() -> None:
    """
    Main function to start the WebSocket server.
    """
    async with websockets.serve(handler, "localhost", 8765):
        logger.info("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Run forever


async def coordinate(q):
    server = asyncio.create_task(websocket_server())
    while True:
        await asyncio.sleep(
            0
        )  # this is necessary to allow the asyncio loop to switch tasks.
        try:
            q.get_nowait()
        except Empty:
            pass
        else:  # block will run whenever there is _any_ message in the queue.
            server.cancel()
            return
    server.cancel()


def run_webscoket_server(q: asyncio.Queue) -> None:
    asyncio.run(coordinate(q))


if __name__ == "__main__":
    asyncio.run(websocket_server())

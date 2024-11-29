from datetime import datetime
from typing import TypedDict
from zoneinfo import ZoneInfo

from make_market.orderbook.core import OrderBook


class RawQuoteDict(TypedDict):
    """A dictionary representing a raw quote."""

    timestamp: str
    bid_prices: list[float]
    ask_prices: list[float]
    bid_sizes: list[int]
    ask_sizes: list[int]


def create_raw_quote_from_orderbook(
    orderbook: OrderBook, timezone: ZoneInfo
) -> RawQuoteDict:
    """
    Create a raw quote dictionary from an order book.

    Args:
        orderbook (OrderBook): The order book from which to create the raw quote.
        timezone (ZoneInfo): The timezone to use for the timestamp.

    Returns:
        RawQuoteDict: A dictionary containing the timestamp and the order book data.

    """
    return {
        "timestamp": datetime.now(timezone).isoformat(),
        **orderbook.to_dict(),
    }

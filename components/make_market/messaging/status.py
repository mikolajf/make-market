from enum import Flag, auto


class QuoteStatus(int, Flag):
    """
    QuoteStatus is an enumeration that represents various statuses of a market quote.

    Attributes:
        MARKET_CLOSED: Indicates that the market is closed.
        CROSSED_PRICE: Indicates that the price has crossed a certain threshold.
        EMPTY_ORDERBOOK: Indicates that the order book is empty.

    """

    MARKET_CLOSED = auto()
    CROSSED_PRICE = auto()
    EMPTY_ORDERBOOK = auto()

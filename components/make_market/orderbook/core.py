from dataclasses import dataclass, field
from random import uniform
from typing import Self, TypedDict


class OrderBookDict(TypedDict):
    """
    OrderBookDict is a TypedDict that represents the structure of an order book.

    Attributes:
        ask_prices (list[float]): A list of prices for the ask orders.
        ask_sizes (list[float]): A list of sizes for the ask orders.
        bid_prices (list[float]): A list of prices for the bid orders.
        bid_sizes (list[float]): A list of sizes for the bid orders.

    """

    ask_prices: list[float]
    ask_sizes: list[float]
    bid_prices: list[float]
    bid_sizes: list[float]


@dataclass
class OrderBook:
    """
    OrderBook represents the state of an order book with ask and bid prices and sizes.

    Attributes:
        ask_prices (list[float]): A list of prices for the ask orders.
        ask_sizes (list[float]): A list of sizes for the ask orders.
        bid_prices (list[float]): A list of prices for the bid orders.
        bid_sizes (list[float]): A list of sizes for the bid orders.

    """

    ask_prices: list[float] = field(default_factory=list)
    ask_sizes: list[float] = field(default_factory=list)
    bid_prices: list[float] = field(default_factory=list)
    bid_sizes: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        """
        Validate the order book to ensure that prices and sizes are consistent.

        Raises:
            ValueError: If ask_prices and ask_sizes or bid_prices and bid_sizes
                        are not of the same length, or if ask_prices are not in
                        strictly increasing order, or if bid_prices are not in
                        strictly decreasing order.

        """
        if len(self.ask_prices) != len(self.ask_sizes):
            msg = "ask_prices and ask_sizes must be of the same length"
            raise ValueError(msg)
        if len(self.bid_prices) != len(self.bid_sizes):
            msg = "bid_prices and bid_sizes must be of the same length"
            raise ValueError(msg)

        # check that prices in ask_prices are in ascending order
        if self.ask_prices != sorted(self.ask_prices):
            msg = "ask_prices must be in strictly increasing order"
            raise ValueError(msg)

        # check that prices in bid_prices are in descending order
        if self.bid_prices != sorted(self.bid_prices, reverse=True):
            msg = "bid_prices must be in strictly decreasing order"
            raise ValueError(msg)

    def is_empty(self) -> bool:
        """
        Check if the order book is empty.

        Returns:
            bool: True if both ask_prices and bid_prices are empty, False otherwise.

        """
        return not (self.ask_prices or self.bid_prices)

    # create class method to create a random orderbook given midprice and spread
    @classmethod
    def random(
        cls,
        midprice: float,
        spread: float,
        n_ask_levels: int = 10,
        n_bid_levels: int = 10,
    ) -> Self:
        """
        Create a random order book given a midprice and spread.

        Args:
            midprice (float): The midprice around which the order book is centered.
            spread (float): The spread between the ask and bid prices.
            n_ask_levels (int, optional): The number of ask levels. Defaults to 10.
            n_bid_levels (int, optional): The number of bid levels. Defaults to 10.

        Returns:
            OrderBook: An instance of OrderBook with random prices and sizes.

        """
        spread_variation = spread * 0.1  # 10% variation in spread

        ask_prices = [
            midprice + (i + 1) * spread + uniform(-spread_variation, spread_variation)  # noqa: S311
            for i in range(n_ask_levels)
        ]
        ask_sizes = [uniform(5.0, 15.0) for _ in range(n_ask_levels)]  # noqa: S311

        bid_prices = [
            midprice - (i + 1) * spread + uniform(-spread_variation, spread_variation)  # noqa: S311
            for i in range(n_bid_levels)
        ]
        bid_sizes = [uniform(5.0, 15.0) for _ in range(n_bid_levels)]  # noqa: S311

        return cls(ask_prices, ask_sizes, bid_prices, bid_sizes)

    @property
    def top_level_prices(self) -> tuple[float | None, float | None]:
        """
        Get the top level ask and bid prices.

        Returns:
            tuple[float | None, float | None]: The top ask price and top bid price, or None if empty.

        """
        top_ask = self.ask_prices[0] if self.ask_prices else None
        top_bid = self.bid_prices[0] if self.bid_prices else None
        return top_ask, top_bid

    @property
    def top_level_spread(self) -> float | None:
        """
        Calculate the top-level spread of the order book.

        The top-level spread is defined as the difference between the top ask price
        and the top bid price. If either the top ask or top bid price is None, the
        function returns None.

        Returns:
            float | None: The top-level spread if both top ask and top bid prices
            are available, otherwise None.

        """
        top_ask, top_bid = self.top_level_prices
        if top_ask is None or top_bid is None:
            return None
        return top_ask - top_bid

    @property
    def mid_price(self) -> float | None:
        """
        Calculate the mid-price of the order book.

        The mid-price is defined as the average of the top ask price and the top bid price.
        If either the top ask price or the top bid price is not available (i.e., None),
        the function returns None.

        Returns:
            float | None: The mid-price if both top ask and top bid prices are available,
                          otherwise None.

        """
        top_ask, top_bid = self.top_level_prices
        if top_ask is None or top_bid is None:
            return None
        return (top_ask + top_bid) / 2

    # create a method to get number of levels in the orderbook,
    # should return a tuple
    @property
    def n_levels(self) -> tuple[int, int]:
        """
        Returns the number of levels in the order book for both ask and bid prices.

        Returns:
            tuple[int, int]: A tuple containing the number of ask price levels and bid price levels.

        """
        return len(self.ask_prices), len(self.bid_prices)

    # create a method to serialize the orderbook to a dictionary
    def to_dict(self) -> OrderBookDict:
        """
        Converts the order book data to a dictionary format.

        Returns:
            OrderBookDict: A dictionary containing the order book data with the following keys:
                - ask_prices: List of ask prices.
                - ask_sizes: List of ask sizes.
                - bid_prices: List of bid prices.
                - bid_sizes: List of bid sizes.

        """
        return OrderBookDict(
            ask_prices=self.ask_prices,
            ask_sizes=self.ask_sizes,
            bid_prices=self.bid_prices,
            bid_sizes=self.bid_sizes,
        )

    # create a method to create an orderbook from a dictionary
    @classmethod
    def from_dict(cls, data: OrderBookDict) -> Self:
        """
        Create an instance of the class from a dictionary.

        Args:
            data (OrderBookDict): A dictionary containing the data to initialize the class instance.

        Returns:
            Self: An instance of the class initialized with the provided data.

        """
        return cls(**data)

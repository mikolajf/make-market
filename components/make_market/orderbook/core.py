import random
from dataclasses import dataclass, field
from typing import Self, TypedDict


class OrderBookDict(TypedDict):
    ask_prices: list[float]
    ask_sizes: list[float]
    bid_prices: list[float]
    bid_sizes: list[float]


@dataclass
class OrderBook:
    ask_prices: list[float] = field(default_factory=list)
    ask_sizes: list[float] = field(default_factory=list)
    bid_prices: list[float] = field(default_factory=list)
    bid_sizes: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if len(self.ask_prices) != len(self.ask_sizes):
            raise ValueError(
                "ask_prices and ask_sizes must be of the same length"
            )
        if len(self.bid_prices) != len(self.bid_sizes):
            raise ValueError(
                "bid_prices and bid_sizes must be of the same length"
            )

        # check that prices in ask_prices are in ascending order
        if self.ask_prices != sorted(self.ask_prices):
            raise ValueError("ask_prices must be in strictly increasing order")

        # check that prices in bid_prices are in descending order
        if self.bid_prices != sorted(self.bid_prices, reverse=True):
            raise ValueError("bid_prices must be in strictly decreasing order")

    def is_empty(self) -> bool:
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
        spread_variation = spread * 0.1  # 10% variation in spread

        ask_prices = [
            midprice
            + (i + 1) * spread
            + random.uniform(-spread_variation, spread_variation)
            for i in range(n_ask_levels)
        ]
        ask_sizes = [random.uniform(5.0, 15.0) for i in range(n_ask_levels)]
        bid_prices = [
            midprice
            - (i + 1) * spread
            + random.uniform(-spread_variation, spread_variation)
            for i in range(n_bid_levels)
        ]
        bid_sizes = [random.uniform(5.0, 15.0) for i in range(n_bid_levels)]

        return cls(ask_prices, ask_sizes, bid_prices, bid_sizes)

    @property
    def top_level_prices(self) -> tuple[float | None, float | None]:
        top_ask = self.ask_prices[0] if self.ask_prices else None
        top_bid = self.bid_prices[0] if self.bid_prices else None
        return top_ask, top_bid

    @property
    def top_level_spread(self) -> float | None:
        top_ask, top_bid = self.top_level_prices
        if top_ask is None or top_bid is None:
            return None
        return top_ask - top_bid

    @property
    def mid_price(self) -> float | None:
        top_ask, top_bid = self.top_level_prices
        if top_ask is None or top_bid is None:
            return None
        return (top_ask + top_bid) / 2

    # create a method to serialize the orderbook to a dictionary
    def to_dict(self) -> OrderBookDict:
        return OrderBookDict(
            ask_prices=self.ask_prices,
            ask_sizes=self.ask_sizes,
            bid_prices=self.bid_prices,
            bid_sizes=self.bid_sizes,
        )

    # create a method to create an orderbook from a dictionary
    @classmethod
    def from_dict(cls, data: OrderBookDict) -> Self:
        return cls(**data)

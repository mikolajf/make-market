import random
from dataclasses import dataclass, field
from typing import Self


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
    def random(cls, midprice: float, spread: float, n_levels: int) -> Self:
        spread_variation = spread * 0.1  # 10% variation in spread

        ask_prices = [
            midprice
            + (i + 1) * spread
            + random.uniform(-spread_variation, spread_variation)
            for i in range(n_levels)
        ]
        ask_sizes = [random.uniform(5.0, 15.0) for i in range(n_levels)]
        bid_prices = [
            midprice
            - (i + 1) * spread
            + random.uniform(-spread_variation, spread_variation)
            for i in range(n_levels)
        ]
        bid_sizes = [random.uniform(5.0, 15.0) for i in range(n_levels)]

        return cls(ask_prices, ask_sizes, bid_prices, bid_sizes)

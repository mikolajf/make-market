from dataclasses import dataclass, field


@dataclass
class OrderBook:
    ask_prices: list[float] = field(default_factory=list)
    ask_sizes: list[float] = field(default_factory=list)
    bid_prices: list[float] = field(default_factory=list)
    bid_sizes: list[float] = field(default_factory=list)

    def __post_init__(self):
        self.validate()

    def validate(self):
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

    def is_empty(self):
        return not (self.ask_prices or self.bid_prices)

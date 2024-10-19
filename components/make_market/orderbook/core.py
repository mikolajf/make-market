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

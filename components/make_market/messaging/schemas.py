import datetime
from dataclasses import dataclass

from dataclasses_avroschema import AvroModel, types


@dataclass
class BaseQuote(AvroModel):
    """
    BaseQuote is a data model representing a market quote with various attributes.

    Attributes:
        symbol (str): The symbol of the financial instrument.
        exchange (str): The exchange where the instrument is traded.
        vendor_timestamp (datetime.datetime): The timestamp provided by the vendor.
        timestamp (datetime.datetime): The local timestamp when the quote was received.
        bid_price (list[int]): A list of bid prices.
        ask_price (list[int]): A list of ask prices.
        price_exponent (int): The exponent used for price scaling.
        bid_size (list[int]): A list of bid sizes.
        ask_size (list[int]): A list of ask sizes.
        size_exponent (int): The exponent used for size scaling.
        app_id (str): The application identifier.
        tick_id (int): The tick identifier.

    """

    symbol: str
    exchange: str

    vendor_timestamp: types.DateTimeMicro
    timestamp: types.DateTimeMicro

    # prices
    bid_price: list[int]
    ask_price: list[int]
    price_exponent: int

    # sizes
    bid_size: list[int]
    ask_size: list[int]
    size_exponent: int

    # ids
    app_id: int
    tick_id: int

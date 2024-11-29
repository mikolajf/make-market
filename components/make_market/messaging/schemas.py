import datetime
from dataclasses import dataclass
from decimal import Decimal

from dataclasses_avroschema import AvroModel, types
from make_market.ws_server.quote import RawQuoteDict


@dataclass
class RawVendorQuote:
    """
    RawVendorQuote is a data model representing a vendor's quote in the market.
    Note that this is only avaialable internally, serialiation at vendor is hidden from us.

    Attributes:
        timestamp (datetime.datetime): The timestamp of the quote.
        bid_prices (list[float]): A list of bid prices.
        ask_prices (list[float]): A list of ask prices.
        bid_sizes (list[int]): A list of bid sizes corresponding to the bid prices.
        ask_sizes (list[int]): A list of ask sizes corresponding to the ask prices.

    """

    timestamp: types.DateTimeMicro

    # prices
    bid_price: list[int]
    ask_price: list[int]
    price_exponent: int

    # sizes
    bid_size: list[int]
    ask_size: list[int]
    size_exponent: int

    @classmethod
    def from_raw_vendor_dict(
        cls, raw_quote_dict: RawQuoteDict, price_exponent: int, size_exponent: int
    ) -> "RawVendorQuote":

        


        # for each price, convert to decimal and store as digits
        for price in raw_quote_dict["bid_prices"]:
            price = Decimal(price)

        return cls(
            timestamp=datetime.datetime.fromisoformat(raw_quote_dict["timestamp"]),
            bid_price=raw_quote_dict["bid_prices"],
            ask_price=raw_quote_dict["ask_prices"],
            price_exponent=2,
            bid_size=raw_quote_dict["bid_sizes"],
            ask_size=raw_quote_dict["ask_sizes"],
            size_exponent=1,
        )


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

    @classmethod
    def from_raw_vendor_data(cls, raw_data: dict) -> "BaseQuote":
        """
        Creates a BaseQuote instance from raw vendor data.

        Args:
            raw_data (dict): The raw data from the vendor.

        Returns:
            BaseQuote: The BaseQuote instance created from the raw data.

        """
        return cls(
            symbol=raw_data["symbol"],
            exchange=raw_data["exchange"],
            vendor_timestamp=datetime.datetime.fromisoformat(
                raw_data["vendor_timestamp"]
            ),
            timestamp=datetime.datetime.fromisoformat(raw_data["timestamp"]),
            bid_price=raw_data["bid_price"],
            ask_price=raw_data["ask_price"],
            price_exponent=raw_data["price_exponent"],
            bid_size=raw_data["bid_size"],
            ask_size=raw_data["ask_size"],
            size_exponent=raw_data["size_exponent"],
            app_id=raw_data["app_id"],
            tick_id=raw_data["tick_id"],
        )

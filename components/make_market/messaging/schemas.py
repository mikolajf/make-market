import datetime
from dataclasses import dataclass

from dataclasses_avroschema import AvroModel, types
from make_market.messaging.decimals import float_to_digits_with_precision
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
        """
        Create a RawVendorQuote instance from a raw vendor dictionary.

        Args:
            raw_quote_dict (RawQuoteDict): The raw quote dictionary containing the quote data.
            price_exponent (int): The exponent to use for price precision.
            size_exponent (int): The exponent to use for size precision.

        Returns:
            RawVendorQuote: An instance of RawVendorQuote populated with the data from the raw quote dictionary.

        """
        return cls(
            timestamp=datetime.datetime.fromisoformat(raw_quote_dict["timestamp"]),
            bid_price=[
                float_to_digits_with_precision(p, price_exponent)
                for p in raw_quote_dict["bid_prices"]
            ],
            ask_price=[
                float_to_digits_with_precision(p, price_exponent)
                for p in raw_quote_dict["ask_prices"]
            ],
            price_exponent=price_exponent,
            bid_size=[
                float_to_digits_with_precision(s, size_exponent)
                for s in raw_quote_dict["bid_sizes"]
            ],
            ask_size=[
                float_to_digits_with_precision(s, size_exponent)
                for s in raw_quote_dict["ask_sizes"]
            ],
            size_exponent=size_exponent,
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
    def from_raw_vendor_quote(  # noqa: PLR0913
        cls,
        raw_quote: RawVendorQuote,
        symbol: str,
        exchange: str,
        timestamp: datetime.datetime,
        app_id: int,
        tick_id: int,
    ) -> "BaseQuote":
        """Create a BaseQuote instance from a RawVendorQuote instance."""
        return cls(
            symbol=symbol,
            exchange=exchange,
            vendor_timestamp=raw_quote.timestamp,
            timestamp=timestamp,
            bid_price=raw_quote.bid_price,
            ask_price=raw_quote.ask_price,
            price_exponent=raw_quote.price_exponent,
            bid_size=raw_quote.bid_size,
            ask_size=raw_quote.ask_size,
            size_exponent=raw_quote.size_exponent,
            app_id=app_id,
            tick_id=tick_id,
        )

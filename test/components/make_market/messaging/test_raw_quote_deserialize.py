import datetime
import math

import pytest
from make_market.messaging.decimals import decimal_from_int_number_with_exponent
from make_market.messaging.schemas import RawVendorQuote
from make_market.orderbook.core import OrderBook
from make_market.settings.models import Settings
from make_market.ws_server.quote import create_raw_quote_from_orderbook


@pytest.fixture
def raw_quote_dict():
    orderbook = OrderBook.random_from_midprice_and_spread(midprice=100.0, spread=2.0)

    return create_raw_quote_from_orderbook(orderbook, timezone=Settings().timezone)


def test_create_raw_vendor_quote_from_dict(raw_quote_dict):
    price_exponent = -6

    quote = RawVendorQuote.from_raw_vendor_dict(
        raw_quote_dict, price_exponent=price_exponent, size_exponent=1
    )

    assert isinstance(
        quote.timestamp, datetime.datetime
    ), "Should be converted to datetime object."

    assert len(quote.ask_price) == len(
        raw_quote_dict["ask_prices"]
    ), "Should have the same length as the raw quote."

    assert math.isclose(
        decimal_from_int_number_with_exponent(quote.ask_price[0], price_exponent),
        raw_quote_dict["ask_prices"][0],
        rel_tol=10**price_exponent,
    ), "Should be converted to the correct price."

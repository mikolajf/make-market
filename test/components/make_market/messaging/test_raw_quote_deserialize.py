import pytest
from make_market.messaging.schemas import RawVendorQuote
from make_market.orderbook.core import OrderBook
from make_market.settings.models import Settings
from make_market.ws_server.quote import create_raw_quote_from_orderbook


@pytest.fixture
def raw_quote_dict():
    orderbook = OrderBook.random_from_midprice_and_spread(midprice=100.0, spread=2.0)

    return create_raw_quote_from_orderbook(orderbook, timezone=Settings().timezone)


def test_create_raw_vendor_quote_from_dict(raw_quote_dict):
    quote = RawVendorQuote(**raw_quote_dict)

    assert quote.timestamp == raw_quote_dict["timestamp"]

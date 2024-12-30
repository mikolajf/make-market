import datetime

import pytest
from make_market.messaging import BaseQuote
from make_market.messaging.status import QuoteStatus
from make_market.settings.models import Settings


@pytest.fixture
def fake_quote() -> BaseQuote:
    return BaseQuote.fake(status=QuoteStatus(0))


def test_base_quote_serialization():
    # Create a BaseQuote instance with dummy data
    quote = BaseQuote(
        symbol="AAPL",
        exchange="NASDAQ",
        vendor_timestamp=datetime.datetime.now(Settings().timezone),
        timestamp=datetime.datetime.now(Settings().timezone),
        bid_price=[100, 101, 102],
        ask_price=[103, 104, 105],
        price_exponent=2,
        bid_size=[10, 20, 30],
        ask_size=[40, 50, 60],
        size_exponent=1,
        app_id=123456,
        tick_id=123456,
    )

    # Serialize the BaseQuote instance to Avro
    avro_data = quote.serialize()

    # Deserialize the Avro data back to a BaseQuote instance
    deserialized_quote = BaseQuote.deserialize(avro_data)

    # Assert that the original and deserialized instances are equal
    assert quote == deserialized_quote


def test_base_quote_fake_data(fake_quote: BaseQuote) -> None:
    # Serialize the fake BaseQuote instance to Avro
    avro_data = fake_quote.serialize()

    # Deserialize the Avro data back to a BaseQuote instance
    deserialized_fake_quote = BaseQuote.deserialize(avro_data)

    # Assert that the original and deserialized instances are equal
    assert fake_quote == deserialized_fake_quote


def test_status_is_preserved(fake_quote: BaseQuote) -> None:
    # status prior to serialization
    status = fake_quote.status

    # Serialize the fake BaseQuote instance to Avro
    avro_data = fake_quote.serialize()

    # Deserialize the Avro data back to a BaseQuote instance
    deserialized_fake_quote = BaseQuote.deserialize(avro_data)

    # assert that the status is preserved
    assert status == deserialized_fake_quote.status


def test_changing_status(fake_quote: BaseQuote) -> None:
    # status prior to serialization
    status = fake_quote.status

    # change the status
    fake_quote.status = status | QuoteStatus.CROSSED_PRICE

    # Serialize the fake BaseQuote instance to Avro
    avro_data = fake_quote.serialize()

    # Deserialize the Avro data back to a BaseQuote instance
    deserialized_fake_quote = BaseQuote.deserialize(avro_data)

    # assert QuoteStatus.CROSSED_PRICE in status
    assert QuoteStatus.CROSSED_PRICE in deserialized_fake_quote.status

    # assert that the status is preserved
    assert status | QuoteStatus.CROSSED_PRICE == deserialized_fake_quote.status


def test_create_quote_with_status() -> None:
    # Create a BaseQuote instance with dummy data
    quote = BaseQuote(
        symbol="AAPL",
        exchange="NASDAQ",
        vendor_timestamp=datetime.datetime.now(Settings().timezone),
        timestamp=datetime.datetime.now(Settings().timezone),
        bid_price=[100, 101, 102],
        ask_price=[103, 104, 105],
        price_exponent=2,
        bid_size=[10, 20, 30],
        ask_size=[40, 50, 60],
        size_exponent=1,
        app_id=123456,
        tick_id=123456,
        status=QuoteStatus.CROSSED_PRICE,
    )

    assert quote.status == QuoteStatus.CROSSED_PRICE

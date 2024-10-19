import pytest
from make_market.orderbook import OrderBook


def test_orderbook_initialization():
    orderbook = OrderBook(
        ask_prices=[100.0, 101.0],
        ask_sizes=[10.0, 15.0],
        bid_prices=[99.0, 98.0],
        bid_sizes=[20.0, 25.0],
    )
    assert orderbook.ask_prices == [100.0, 101.0]
    assert orderbook.ask_sizes == [10.0, 15.0]
    assert orderbook.bid_prices == [99.0, 98.0]
    assert orderbook.bid_sizes == [20.0, 25.0]


def test_orderbook_validation_success():
    orderbook = OrderBook(
        ask_prices=[100.0],
        ask_sizes=[10.0],
        bid_prices=[99.0],
        bid_sizes=[20.0],
    )
    assert orderbook.validate() is None
    assert orderbook.ask_prices == [100.0]
    assert orderbook.ask_sizes == [10.0]
    assert orderbook.bid_prices == [99.0]
    assert orderbook.bid_sizes == [20.0]


def test_orderbook_validation_failure_ask():
    with pytest.raises(
        ValueError,
        match="ask_prices and ask_sizes must be of the same length",
    ):
        OrderBook(
            ask_prices=[100.0, 101.0],
            ask_sizes=[10.0],
            bid_prices=[99.0],
            bid_sizes=[20.0],
        )


def test_orderbook_validation_failure_bid():
    with pytest.raises(
        ValueError,
        match="bid_prices and bid_sizes must be of the same length",
    ):
        OrderBook(
            ask_prices=[100.0],
            ask_sizes=[10.0],
            bid_prices=[99.0, 98.0],
            bid_sizes=[20.0],
        )


def test_orderbook_empty_initialization():
    orderbook = OrderBook()
    assert orderbook.ask_prices == []
    assert orderbook.ask_sizes == []
    assert orderbook.bid_prices == []
    assert orderbook.bid_sizes == []
    assert orderbook.is_empty()


def test_orderbook_partial_initialization():
    orderbook = OrderBook(ask_prices=[100.0], ask_sizes=[10.0])
    assert orderbook.ask_prices == [100.0]
    assert orderbook.ask_sizes == [10.0]
    assert orderbook.bid_prices == []
    assert orderbook.bid_sizes == []


def test_orderbook_non_increasing_ask_prices():
    with pytest.raises(
        ValueError,
        match="ask_prices must be in strictly increasing order",
    ):
        OrderBook(
            ask_prices=[101.0, 100.0],
            ask_sizes=[10.0, 15.0],
            bid_prices=[99.0, 98.0],
            bid_sizes=[20.0, 25.0],
        )


def test_orderbook_non_increasing_bid_prices():
    with pytest.raises(
        ValueError,
        match="bid_prices must be in strictly decreasing order",
    ):
        OrderBook(
            ask_prices=[100.0, 101.0],
            ask_sizes=[10.0, 15.0],
            bid_prices=[98.0, 99.0],
            bid_sizes=[20.0, 25.0],
        )

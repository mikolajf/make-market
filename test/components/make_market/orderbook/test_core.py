import pytest
from make_market.orderbook import OrderBook, OrderBookDict


def test_orderbook_initialization() -> None:
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


def test_orderbook_validation_success() -> None:
    orderbook = OrderBook(
        ask_prices=[100.0],
        ask_sizes=[10.0],
        bid_prices=[99.0],
        bid_sizes=[20.0],
    )

    assert orderbook.ask_prices == [100.0]
    assert orderbook.ask_sizes == [10.0]
    assert orderbook.bid_prices == [99.0]
    assert orderbook.bid_sizes == [20.0]


def test_orderbook_validation_failure_ask() -> None:
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


def test_orderbook_validation_failure_bid() -> None:
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


def test_orderbook_empty_initialization() -> None:
    orderbook = OrderBook()
    assert orderbook.ask_prices == []
    assert orderbook.ask_sizes == []
    assert orderbook.bid_prices == []
    assert orderbook.bid_sizes == []
    assert orderbook.is_empty()


def test_orderbook_partial_initialization() -> None:
    orderbook = OrderBook(ask_prices=[100.0], ask_sizes=[10.0])
    assert orderbook.ask_prices == [100.0]
    assert orderbook.ask_sizes == [10.0]
    assert orderbook.bid_prices == []
    assert orderbook.bid_sizes == []


def test_orderbook_non_increasing_ask_prices() -> None:
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


def test_orderbook_non_increasing_bid_prices() -> None:
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


def test_orderbook_random_creation() -> None:
    orderbook1 = OrderBook.random_from_midprice_and_spread(midprice=100.0, spread=1.0)
    orderbook2 = OrderBook.random_from_midprice_and_spread(midprice=100.0, spread=1.0)

    assert orderbook1 != orderbook2
    assert orderbook1.ask_prices != orderbook2.ask_prices
    assert orderbook1.ask_sizes != orderbook2.ask_sizes
    assert orderbook1.bid_prices != orderbook2.bid_prices
    assert orderbook1.bid_sizes != orderbook2.bid_sizes


def test_orderbook_top_level_prices_two_sided() -> None:
    orderbook = OrderBook(
        ask_prices=[100.0, 101.0],
        ask_sizes=[10.0, 15.0],
        bid_prices=[99.0, 98.0],
        bid_sizes=[20.0, 25.0],
    )
    top_ask, top_bid = orderbook.top_level_prices
    assert top_ask == 100.0
    assert top_bid == 99.0


def test_orderbook_top_level_prices_one_sided_ask() -> None:
    orderbook = OrderBook(
        ask_prices=[100.0, 101.0],
        ask_sizes=[10.0, 15.0],
    )
    top_ask, top_bid = orderbook.top_level_prices
    assert top_ask == 100.0
    assert top_bid is None


def test_orderbook_top_level_prices_one_sided_bid() -> None:
    orderbook = OrderBook(
        bid_prices=[99.0, 98.0],
        bid_sizes=[20.0, 25.0],
    )
    top_ask, top_bid = orderbook.top_level_prices
    assert top_ask is None
    assert top_bid == 99.0


def test_orderbook_top_level_prices_empty() -> None:
    orderbook = OrderBook()
    top_ask, top_bid = orderbook.top_level_prices
    assert top_ask is None
    assert top_bid is None


def test_orderbook_top_level_spread_two_sided() -> None:
    orderbook = OrderBook(
        ask_prices=[100.0, 101.0],
        ask_sizes=[10.0, 15.0],
        bid_prices=[99.0, 98.0],
        bid_sizes=[20.0, 25.0],
    )
    spread = orderbook.top_level_spread
    assert spread == 1.0


def test_orderbook_top_level_spread_one_sided_ask() -> None:
    orderbook = OrderBook(
        ask_prices=[100.0, 101.0],
        ask_sizes=[10.0, 15.0],
    )
    assert orderbook.top_level_spread is None


def test_orderbook_top_level_spread_one_sided_bid() -> None:
    orderbook = OrderBook(
        bid_prices=[99.0, 98.0],
        bid_sizes=[20.0, 25.0],
    )
    assert orderbook.top_level_spread is None


def test_orderbook_top_level_spread_empty() -> None:
    orderbook = OrderBook()
    assert orderbook.top_level_spread is None


def test_orderbook_mid_price_two_sided() -> None:
    orderbook = OrderBook(
        ask_prices=[100.0, 101.0],
        ask_sizes=[10.0, 15.0],
        bid_prices=[99.0, 98.0],
        bid_sizes=[20.0, 25.0],
    )
    assert orderbook.mid_price == 99.5


def test_orderbook_mid_price_one_sided_ask() -> None:
    orderbook = OrderBook(
        ask_prices=[100.0, 101.0],
        ask_sizes=[10.0, 15.0],
    )
    assert orderbook.mid_price is None


def test_orderbook_mid_price_one_sided_bid() -> None:
    orderbook = OrderBook(
        bid_prices=[99.0, 98.0],
        bid_sizes=[20.0, 25.0],
    )
    assert orderbook.mid_price is None


def test_orderbook_mid_price_empty() -> None:
    orderbook = OrderBook()
    assert orderbook.mid_price is None


def test_orderbook_to_dict() -> None:
    orderbook = OrderBook(
        ask_prices=[100.0, 101.0],
        ask_sizes=[10.0, 15.0],
        bid_prices=[99.0, 98.0],
        bid_sizes=[20.0, 25.0],
    )
    expected_dict = {
        "ask_prices": [100.0, 101.0],
        "ask_sizes": [10.0, 15.0],
        "bid_prices": [99.0, 98.0],
        "bid_sizes": [20.0, 25.0],
    }
    assert orderbook.to_dict() == expected_dict


def test_orderbook_from_dict() -> None:
    data: OrderBookDict = {
        "ask_prices": [100.0, 101.0],
        "ask_sizes": [10.0, 15.0],
        "bid_prices": [99.0, 98.0],
        "bid_sizes": [20.0, 25.0],
    }
    orderbook = OrderBook.from_dict(data)
    assert orderbook.ask_prices == [100.0, 101.0]
    assert orderbook.ask_sizes == [10.0, 15.0]
    assert orderbook.bid_prices == [99.0, 98.0]
    assert orderbook.bid_sizes == [20.0, 25.0]


def test_orderbook_n_levels() -> None:
    orderbook = OrderBook(
        ask_prices=[100.0, 101.0, 102.0],
        ask_sizes=[10.0, 15.0, 20.0],
        bid_prices=[99.0, 98.0],
        bid_sizes=[20.0, 25.0],
    )
    assert orderbook.n_levels == (3, 2)


def test_empty_orderbook_n_levels() -> None:
    empty_orderbook = OrderBook()
    assert empty_orderbook.n_levels == (0, 0)

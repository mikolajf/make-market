from make_market.messaging.status import QuoteStatus


def test_quote_status_combination():
    combined_status = QuoteStatus.MARKET_CLOSED | QuoteStatus.CROSSED_PRICE
    assert combined_status == (QuoteStatus.MARKET_CLOSED | QuoteStatus.CROSSED_PRICE)
    assert isinstance(combined_status, QuoteStatus)
    assert QuoteStatus.MARKET_CLOSED in combined_status


def test_ok_status():
    status = QuoteStatus(0)

    assert status == QuoteStatus(0)
    assert not bool(status)


def test_starting_with_ok_then_editing():
    status = QuoteStatus(0)
    status |= QuoteStatus.CROSSED_PRICE

    assert status == QuoteStatus.CROSSED_PRICE
    assert QuoteStatus.CROSSED_PRICE in status
    assert QuoteStatus.EMPTY_ORDERBOOK not in status
    assert bool(status)


def test_above_max():
    # testing with value that is not mapped to any status
    status = QuoteStatus(1 << 10)
    assert status.value == 1 << 10

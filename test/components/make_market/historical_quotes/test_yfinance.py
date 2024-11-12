from make_market.historical_quotes.yfinance import get_bid_and_ask_from_yfinance


def test_get_bid_and_ask_from_yfinance():
    # Arrange
    ticker_symbol = "EURUSD=X"

    # Act
    bid, ask = get_bid_and_ask_from_yfinance(ticker_symbol)

    # Assert
    assert bid != 0.0
    assert ask != 0.0

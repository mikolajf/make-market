import pytest


@pytest.mark.skip(reason="This test is not working in the CI/CD pipeline")
def test_get_bid_and_ask_from_yfinance():
    # I put this import inside test function as it breaks the test if it's not installed / behind firewall
    from make_market.historical_quotes.yfinance import get_bid_and_ask_from_yfinance

    # Arrange
    ticker_symbol = "EURUSD=X"

    # Act
    bid, ask = get_bid_and_ask_from_yfinance(ticker_symbol)

    # Assert
    assert bid != 0.0
    assert ask != 0.0

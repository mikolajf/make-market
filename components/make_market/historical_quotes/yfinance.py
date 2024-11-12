import yfinance as yf

from . import logger


def get_bid_and_ask_from_yfinance(ticker: str) -> tuple[float, float]:
    """
    Get bid and ask prices for a given ticker using yfinance.

    Args:
        ticker (str): The ticker symbol to get bid and ask prices for.

    Returns:
        tuple[float, float]: A tuple containing the bid and ask prices.

    """
    logger.info(f"Getting bid and ask prices for {ticker} from yfinance.")

    data = yf.Ticker(ticker)
    bid = data.info["bid"]
    ask = data.info["ask"]
    return bid, ask

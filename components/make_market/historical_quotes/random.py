import random

from . import logger


def get_random_bid_and_ask(reference_data_ticker: str) -> tuple[float, float]:
    """
    Generate random bid and ask prices based on a reference ticker.

    Args:
        reference_data_ticker (str): The ticker symbol for the reference data.

    Returns:
        tuple[float, float]: A tuple containing the bid and ask prices.

    """
    logger.info(f"Generating random bid and ask prices for {reference_data_ticker}.")

    mid_price = random.randint(150, 250)  # noqa: S311
    spread = random.random() * 5  # noqa: S311
    bid = mid_price - spread // 2
    ask = mid_price + spread // 2
    return bid, ask

from typing import Protocol


class MarketDataProtocol(Protocol):
    """
    MarketDataProtocol is a protocol that defines a callable interface for fetching market data.
    """

    def __call__(self, reference_data_ticker: str) -> tuple[float, float]:
        """
        Invokes the instance with the given reference data ticker.

        Args:
            reference_data_ticker (str): The ticker symbol for the reference data.

        Returns:
            Tuple[float, float]: A tuple containing two float values.

        """
        ...

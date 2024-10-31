from make_market.log.core import get_logger

logger = get_logger(__name__)

# relative imports
from make_market.historical_quotes.protocol import MarketDataProtocol
from make_market.historical_quotes.random import get_random_bid_and_ask

__all__ = ["MarketDataProtocol", "get_random_bid_and_ask"]

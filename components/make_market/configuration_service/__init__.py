import asyncio
from collections.abc import AsyncIterator

from make_market.log.core import get_logger
from make_market.producer_consumer.protocols import (
    ConfigListenerProtocol,
    ConfigurationServiceProtocol,
)

logger = get_logger(__name__)


async def dummy_config_change_generator() -> AsyncIterator[dict[str, bool]]:
    """
    An asynchronous generator that yields configuration changes.

    This generator simulates configuration changes by yielding a dictionary
    with a key "active" and a boolean value. It waits for 1 second between
    each yield.

    Yields:
        dict: A dictionary with a single key "active" and a boolean value.

    """
    try:
        await asyncio.sleep(1)
        yield {"EUR/USD": True}
        await asyncio.sleep(1)
        yield {"JPY/USD": True, "EUR/USD": True}
        await asyncio.sleep(1)
        yield {}
        await asyncio.sleep(1)
        yield {"EUR/USD": True}
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        logger.info("KeyboardInterrupt, stopping ConfigurationService")


class ConfigurationService(ConfigurationServiceProtocol):  # noqa: D101
    def __init__(self, async_watch_function=dummy_config_change_generator):
        self.config = {"EUR/USD": True, "GBP/USD": True}
        self.async_watch_function = async_watch_function()
        self.listeners: list[ConfigListenerProtocol] = []

    def register_listener(self, listener: ConfigListenerProtocol) -> None:  # noqa: D102
        self.listeners.append(listener)

    # TODO: this should implement start/stop methods

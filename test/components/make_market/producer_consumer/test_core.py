import asyncio
import contextlib
import random
from collections.abc import AsyncIterator

import pytest
from make_market.log.core import get_logger
from make_market.producer_consumer import (
    ConfigurationServiceProtocol,
    ConsumerProtocol,
    ProducerProtocol,
)

logger = get_logger("test_logger")


async def dummy_config_change_generator() -> AsyncIterator[dict[str, bool]]:
    """
    An asynchronous generator that yields configuration changes.

    This generator simulates configuration changes by yielding a dictionary
    with a key "active" and a boolean value. It waits for 1 second between
    each yield.

    Yields:
        dict: A dictionary with a single key "active" and a boolean value.

    """
    for _ in range(2):
        await asyncio.sleep(1)
        yield {"active": random.choice([True, False])}


class ConfigurationService(ConfigurationServiceProtocol):
    def __init__(self, async_watch_function=dummy_config_change_generator):
        self.config = {"active": True}
        self.async_watch_function = async_watch_function()
        self.listeners: list[ProducerProtocol] = []

    def register_listener(self, listener: ProducerProtocol) -> None:
        self.listeners.append(listener)


class Producer(ProducerProtocol):
    def __init__(
        self, queue: asyncio.Queue, config_service: ConfigurationServiceProtocol
    ):
        self.queue = queue
        self.config_service = config_service
        self.active = True
        self.config_service.register_listener(self)

    async def connect(self) -> None:
        logger.info("Connected to WebSocket")

    async def disconnect(self) -> None:
        logger.info("Disconnected from WebSocket")

    async def produce(self) -> None:
        await self.connect()
        while True:
            if self.active:
                data = random.randint(1, 100)  # Simulate receiving data from WebSocket
                logger.info(f"Produced: {data}")
                await self.queue.put(data)
            await asyncio.sleep(1)  # Simulate time delay

    async def on_config_change(self, config: dict) -> None:
        self.active = config["active"]
        if self.active:
            await self.connect()
        else:
            await self.disconnect()


@pytest.mark.asyncio
async def test_configuration_service():
    config_service = ConfigurationService()
    assert config_service.config["active"] is True

    class ProducerMock(ProducerProtocol):
        async def on_config_change(self, config: dict) -> None:
            logger.info(f"Received config change: {config}")

        async def connect(self) -> None:
            raise NotImplementedError

        async def disconnect(self) -> None:
            raise NotImplementedError

        async def produce(self) -> None:
            raise NotImplementedError

    config_service.register_listener(ProducerMock())
    await config_service.subscribe_to_config_changes()
    del config_service


@pytest.mark.asyncio
async def test_producer_responds_to_config_changes():
    queue = asyncio.Queue()
    config_service = ConfigurationService()
    producer = Producer(queue, config_service)

    await producer.connect()
    assert producer.active is True

    await producer.on_config_change({"active": False})
    assert producer.active is False

    await producer.on_config_change({"active": True})
    assert producer.active is True


@pytest.mark.asyncio
async def test_producer_produces_data():
    queue = asyncio.Queue()
    config_service = ConfigurationService()
    producer = Producer(queue, config_service)

    async def produce_data():
        await producer.produce()

    # Run the producer in the background
    producer_task = asyncio.create_task(produce_data())

    # Allow some time for the producer to produce data
    await asyncio.sleep(2)

    # Check if the queue has data
    assert not queue.empty()

    # Retrieve data from the queue and check if it's within the expected range
    data = await queue.get()
    assert 1 <= data <= 100

    # Cancel the producer task to clean up
    producer_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await producer_task


@pytest.mark.asyncio
async def test_consumer():
    queue = asyncio.Queue()

    class Consumer(ConsumerProtocol):
        def __init__(self, queue: asyncio.Queue, consumer_id: int):
            self.queue = queue
            self.consumer_id = consumer_id

        async def consume(self) -> None:
            while True:
                data = await self.get_data()
                logger.info(f"Consumer {self.consumer_id} consumed: {data}")
                assert data > 0

        async def get_data(self) -> int:
            while self.queue.empty():
                await asyncio.sleep(0.1)
            return await self.queue.get()

    consumer = Consumer(queue, 1)

    await queue.put(42)
    data = await consumer.get_data()
    assert data == 42

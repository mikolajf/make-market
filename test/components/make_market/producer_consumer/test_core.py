import asyncio
import random

import pytest
from make_market.producer_consumer import (
    ConfigurationServiceProtocol,
    ConsumerProtocol,
    ProducerProtocol,
)


class ConfigurationService(ConfigurationServiceProtocol):
    def __init__(self):
        self.config = {"active": True}
        self.listeners: list[ProducerProtocol] = []

    def register_listener(self, listener: ProducerProtocol) -> None:
        self.listeners.append(listener)

    async def simulate_config_changes(self) -> None:
        await asyncio.sleep(1)  # Simulate time delay for config changes
        self.config["active"] = False
        print(f"Configuration changed: {self.config}")
        for listener in self.listeners:
            await listener.on_config_change(self.config)


class Producer(ProducerProtocol):
    def __init__(
        self, queue: asyncio.Queue, config_service: ConfigurationServiceProtocol
    ):
        self.queue = queue
        self.config_service = config_service
        self.active = True
        self.config_service.register_listener(self)

    async def connect(self) -> None:
        # Simulate WebSocket connection
        await asyncio.sleep(1)
        print("Connected to WebSocket")

    async def disconnect(self) -> None:
        # Simulate WebSocket disconnection
        await asyncio.sleep(1)
        print("Disconnected from WebSocket")

    async def produce(self) -> None:
        await self.connect()
        while True:
            if self.active:
                data = random.randint(
                    1, 100
                )  # Simulate receiving data from WebSocket
                print(f"Produced: {data}")
                self.queue.put(data)
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
            assert config["active"] is False
            pytest.exit(returncode=0)

        async def connect(self) -> None:
            raise NotImplementedError

        async def disconnect(self) -> None:
            raise NotImplementedError

        async def produce(self) -> None:
            raise NotImplementedError

    config_service.register_listener(ProducerMock())
    await config_service.simulate_config_changes()


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
async def test_consumer():
    queue = asyncio.Queue()

    class Consumer(ConsumerProtocol):
        def __init__(self, queue: asyncio.Queue, consumer_id: int):
            self.queue = queue
            self.consumer_id = consumer_id

        async def consume(self) -> None:
            while True:
                data = await self.get_data()
                print(f"Consumer {self.consumer_id} consumed: {data}")
                assert data > 0

        async def get_data(self) -> int:
            while self.queue.empty():
                await asyncio.sleep(0.1)
            return self.queue.get()

    consumer = Consumer(queue, 1)

    await queue.put(42)
    data = await consumer.get_data()

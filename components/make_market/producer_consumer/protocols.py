# Protocols
from collections.abc import AsyncIterator
from typing import Protocol


class StartableStopable(Protocol):
    """
    Protocol for objects that can be started and stopped.
    Classes implementing this protocol should provide implementations for the following methods:
    - start: Method to start the object.
    - stop: Method to stop the object.
    """

    def start(self) -> None:
        """
        Starts the producer or consumer process.

        This method should be implemented by subclasses to define the specific
        behavior when the process is started.

        Returns:
            None

        """
        ...

    def stop(self) -> None:
        """
        Stops the current process or operation.

        This method is intended to be overridden by subclasses to implement
        specific stop functionality. It does not take any parameters and does
        not return any value.
        """
        ...


class ConfigListenerProtocol(Protocol):
    """
    ConfigListenerProtocol defines the interface for a listener that handles configuration changes.
    """

    async def on_config_change(self, config: dict) -> None:
        """
        Asynchronously handles configuration changes.

        Args:
            config (dict): A dictionary containing the new configuration settings.

        Returns:
            None

        """
        ...


class ConfigurationServiceProtocol(Protocol):
    """
    A protocol that defines the configuration service interface.
    The ConfigurationServiceProtocol is designed to manage configuration listeners
    and simulate configuration changes. It provides methods to register listeners
    that adhere to the ProducerProtocol and to simulate configuration changes
    asynchronously.
    """

    async_watch_function: AsyncIterator
    listeners: list[ConfigListenerProtocol]

    def __init__(self, async_watch_function: AsyncIterator) -> None:
        self.async_watch_function = async_watch_function()
        self.listeners: list[ConfigListenerProtocol] = []

    def register_listener(self, listener: "ConfigListenerProtocol") -> None:
        """
        Registers a listener that adheres to the ProducerProtocol.

        Args:
            listener (ProducerProtocol): The listener to be registered.

        """
        ...

    async def subscribe_to_config_changes(self) -> None:
        """
        Simulates configuration changes asynchronously.

        This method is intended to mimic the behavior of configuration changes
        in a controlled environment. It does not take any parameters and does
        not return any value.

        Returns:
            None

        """
        while True:
            try:
                change = await self.async_watch_function.__anext__()
            except StopAsyncIteration:
                break

            for listener in self.listeners:
                await listener.on_config_change(change)


class ProducerProtocol(Protocol):
    """
    ProducerProtocol is an asynchronous protocol that defines the methods required
    for establishing and terminating connections, producing items or data, and
    handling configuration changes.
    """

    async def connect(self) -> None:
        """
        Establishes an asynchronous connection.

        This method should be implemented to handle the logic for connecting
        to a specific service or resource asynchronously.

        Raises:
            ConnectionError: If the connection attempt fails.

        """
        ...

    async def disconnect(self) -> None:
        """
        Asynchronously disconnects the current connection.

        This method should be implemented to handle the disconnection logic
        for the specific protocol being used. It ensures that any necessary
        cleanup or resource release is performed when the connection is terminated.

        Returns:
            None

        """
        ...

    async def produce(self) -> None:
        """
        Asynchronously produces items or data.

        This method is intended to be overridden by subclasses to implement
        the specific logic for producing items or data in an asynchronous manner.

        Returns:
            None

        """
        ...

    async def producer_generator(self) -> AsyncIterator[bytes]:
        """
        Asynchronously generates items or data.

        This method is intended to be overridden by subclasses to implement
        the specific logic for generating items or data in an asynchronous manner.

        Yields:
            Any: The items or data generated.

        """
        ...

    async def on_config_change(self, config: dict) -> None:
        """
        Asynchronously handles configuration changes.

        This method is called when there is a change in the configuration.

        Args:
            config (dict): A dictionary containing the new configuration settings.

        Returns:
            None

        """
        ...


class ConsumerProtocol(Protocol):
    """
    ConsumerProtocol is an abstract base class that defines the protocol for consuming messages
    and retrieving data asynchronously.
    """

    async def consume(self) -> None:
        """
        Consumes messages from a queue or stream.

        This coroutine method is responsible for consuming messages from a specified
        queue or stream. The implementation details should handle the retrieval and
        processing of messages asynchronously.

        Raises:
            NotImplementedError: If the method is not implemented.

        """
        ...

    async def get_data(self) -> int:
        """
        Asynchronously retrieves data.

        Returns:
            int: The data retrieved.

        """
        ...


class AppProtocol(Protocol):
    """
    AppProtocol defines the interface for an application that manages configuration,
    a single producer, and multiple consumers.
    """

    def __init__(
        self,
        config_service: ConfigurationServiceProtocol,
        producer: ProducerProtocol,
        consumers: list[ConsumerProtocol],
    ) -> None:
        """
        Initializes the AppProtocol with the given configuration service, producer, and consumers.

        Args:
            config_service (ConfigurationServiceProtocol): The configuration service.
            producer (ProducerProtocol): The producer.
            consumers (list[ConsumerProtocol]): A list of consumers.

        """
        self.config_service = config_service
        self.producer = producer
        self.consumers = consumers

    async def start(self) -> None:
        """
        Starts the application by connecting the producer and consumers,
        and subscribing to configuration changes.

        Returns:
            None

        """
        await self.producer.connect()
        for consumer in self.consumers:
            await consumer.consume()
        await self.config_service.subscribe_to_config_changes()

    async def stop(self) -> None:
        """
        Stops the application by disconnecting the producer and consumers.

        Returns:
            None

        """
        await self.producer.disconnect()
        for consumer in self.consumers:
            await consumer.get_data()

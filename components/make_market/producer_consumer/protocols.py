# Protocols
from typing import Protocol


class ConfigurationServiceProtocol(Protocol):
    """
    A protocol that defines the configuration service interface.
    The ConfigurationServiceProtocol is designed to manage configuration listeners
    and simulate configuration changes. It provides methods to register listeners
    that adhere to the ProducerProtocol and to simulate configuration changes
    asynchronously.
    """

    def register_listener(self, listener: "ProducerProtocol") -> None:
        """
        Registers a listener that adheres to the ProducerProtocol.

        Args:
            listener (ProducerProtocol): The listener to be registered.

        """
        ...

    async def simulate_config_changes(self) -> None:
        """
        Simulates configuration changes asynchronously.

        This method is intended to mimic the behavior of configuration changes
        in a controlled environment. It does not take any parameters and does
        not return any value.

        Returns:
            None

        """
        ...


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

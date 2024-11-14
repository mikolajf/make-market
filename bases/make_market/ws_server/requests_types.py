from enum import StrEnum
from typing import TypedDict


class Actions(StrEnum):
    """Enumeration for possible actions in the WebSocket server."""

    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


class Request(TypedDict):
    """
    Request is a TypedDict that represents the structure of a request in the system.

    Attributes:
        action (Actions): The action to be performed, represented by an instance of the Actions enum.
        symbol (str): The symbol associated with the request, typically representing a financial instrument.

    """

    action: Actions
    symbol: str

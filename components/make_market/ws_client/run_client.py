import asyncio
import threading

import zmq
from make_market.configuration_service import ConfigurationService
from make_market.producer_consumer.zero_mq import PubSubWithZeroMQ
from make_market.settings.models import Settings
from make_market.ws_client.client import WebSocketConnectAsync


def _dummy_subscriber(socket: zmq.Socket, sub_id: int) -> None:
    while True:
        message = socket.recv_string()
        print(f"Subscriber {sub_id} received: {message}")  # noqa: T201


if __name__ == "__main__":
    ps = PubSubWithZeroMQ(
        in_address="tcp://localhost:5555", out_address="tcp://localhost:5556"
    )
    ps.start()

    sub_thread1 = threading.Thread(
        target=_dummy_subscriber, args=(ps.subscriber_socket, 1)
    )
    sub_thread2 = threading.Thread(
        target=_dummy_subscriber, args=(ps.subscriber_socket, 2)
    )

    sub_thread1.start()
    sub_thread2.start()

    config_service = ConfigurationService()

    # init client
    url = Settings().vendor_websocket.URL
    client = WebSocketConnectAsync(
        url, config=config_service.config, publisher_socket=ps.async_publisher_socket
    )
    config_service.register_listener(client)

    async def _main_for_testing():
        try:
            await asyncio.gather(
                client.start(), config_service.subscribe_to_config_changes()
            )
        except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
            # TODO: this does not close properly
            await asyncio.wait_for(client.stop(), timeout=1)

    asyncio.run(_main_for_testing())

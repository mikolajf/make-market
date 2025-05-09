from functools import partial
from random import randint
from string import ascii_uppercase as uppercase

from make_market.producer_consumer.zero_mq import PubSubWithZeroMQ
from make_market.ws_client.client import WebSocketConnectAsync


def random_int_producer() -> bytes:
    string = "%s-%05d" % (uppercase[randint(0, 9)], randint(0, 100000))
    yield string.encode('utf-8')

def message_printer(message: bytes, id: int) -> None:
    print(f"Subscriber {id}: {message.decode('utf-8')}")

def main() -> None:

    websocket_client = WebSocketConnectAsync(url=settings.URL)
    websocket_client.connect()

    pubsub = PubSubWithZeroMQ()
    pubsub.start_publishers(publishers=[random_int_producer])
    pubsub.start_subscribers(subscribers=[partial(message_printer, id=i) for i in range(3)])
    pubsub.start_proxy()
    # pubsub.start_async_client()


if __name__ == '__main__':
    main()

from functools import partial
from random import randint
from string import ascii_uppercase as uppercase

from make_market.producer_consumer.zero_mq import PubSubWithZeroMQ
from make_market.settings.models import Settings
from make_market.ws_client.client import WebSocketConnectAsync

# fetch settings from central store
settings = Settings().vendor_websocket

def random_int_producer() -> bytes:
    string = "%s-%05d" % (uppercase[randint(0, 9)], randint(0, 100000))
    return string.encode('utf-8')

def message_printer(message: bytes, id: int) -> None:
    print(f"Subscriber {id}: {message.decode('utf-8')}")

import asyncio


def start_webscoket_sublisher_in_separate_thread(websocket_client):
    pass


async def main() -> None:
    settings = Settings().vendor_websocket
    websocket_client = WebSocketConnectAsync(url=settings.URL)
    websocket_client.connect()

    pubsub = PubSubWithZeroMQ()
    pubsub.start_publishers(publishers=[websocket_client.producer_generator])
    pubsub.start_subscribers(subscribers=[partial(message_printer, id=i) for i in range(3)])
    pubsub.setup_proxy()
    asyncio.run(main())

if __name__ == '__main__':
    asyncio.run(main())

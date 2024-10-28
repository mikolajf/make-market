import asyncio

import motor.motor_asyncio
from beanie import init_beanie  # type: ignore
from make_market.log.core import get_logger
from make_market.product_config.schema import Listing, ProductConfig
from make_market.settings.models import Settings

settings = Settings().config_database
logger = get_logger("product_config")


async def init() -> None:
    client = motor.motor_asyncio.AsyncIOMotorClient(  # type: ignore
        f"mongodb://{settings.host}:{settings.port}"
    )

    logger.info("Initalizing schema")
    # Initialize beanie with the ProductConfig document class and a database
    await init_beanie(database=client.products, document_models=[ProductConfig])  # type: ignore

    eur_usd = ProductConfig(
        symbol_name="EURUSD",
        decimal_places=5,
        listings=[
            Listing(provider_name="Provider1", subscription_symbol="EURUSD_1"),
            Listing(provider_name="Provider2", subscription_symbol="EURUSD_2"),
        ],
        enabled=True,
    )

    await eur_usd.insert()
    logger.info("ProductConfig document inserted")


asyncio.run(init())

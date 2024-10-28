import motor.motor_asyncio
from beanie import init_beanie  # type: ignore  # noqa: PGH003
from make_market.log.core import get_logger
from make_market.product_config.schema import ProductConfig
from make_market.settings.models import Settings

settings = Settings().config_database
logger = get_logger("product_config")


# TODO: we would need to call this function in the main application
async def setup_database() -> None:
    """
    Asynchronously sets up the database connection and initializes the schema.

    This function connects to a MongoDB instance using the motor_asyncio client
    and initializes the Beanie ODM with the specified document models.

    Raises:
        MotorClientError: If there is an issue connecting to the MongoDB instance.
        BeanieInitializationError: If there is an issue initializing the Beanie ODM.

    """
    client = motor.motor_asyncio.AsyncIOMotorClient(  # type: ignore  # noqa: PGH003
        f"mongodb://{settings.host}:{settings.port}",
        directConnection=True,  # this is required for replica sets
    )

    logger.info("Initalizing schema")
    # Initialize beanie with the ProductConfig document class and a database
    await init_beanie(
        database=client.get_database(settings.database_name),
        document_models=[ProductConfig],
    )  # type: ignore  # noqa: PGH003

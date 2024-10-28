import asyncio
import datetime
from enum import StrEnum
from typing import TypedDict

import motor.motor_asyncio
import pymongo.errors
from bson import ObjectId, Timestamp
from make_market.log.core import get_logger
from make_market.product_config.schema import ProductConfig
from make_market.settings.models import Settings

logger = get_logger("__name__")

settings = Settings().config_database


class OperationType(StrEnum):
    """
    Enum representing the types of operations in MongoDB change streams.
    """

    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


class Namespace(TypedDict):
    """
    TypedDict representing the namespace of a MongoDB collection.
    """

    db: str
    coll: str


class DocumentKey(TypedDict):
    """
    TypedDict representing the document key in a MongoDB collection.
    """

    _id: ObjectId


class UpdateDescription(TypedDict):
    """
    TypedDict representing the update description in a MongoDB change event.
    """

    updatedFields: dict  # type: ignore  # noqa: PGH003
    removedFields: list[str]
    truncatedArrays: list[str]


class ChangeEvent(TypedDict):
    """
    TypedDict representing a change event in a MongoDB collection.
    """

    _id: dict  # type: ignore  # noqa: PGH003
    operationType: str
    clusterTime: Timestamp
    wallTime: datetime.datetime
    fullDocument: ProductConfig | None
    ns: Namespace
    documentKey: DocumentKey
    updateDescription: UpdateDescription | None


async def watch_collection() -> None:
    """
    Watches a MongoDB collection for changes and logs them.

    This function establishes a connection to a MongoDB database using the
    motor_asyncio.AsyncIOMotorClient. It sets up a change stream to watch for
    changes in the specified collection. If a change is detected, it logs the
    change and updates the resume token. In case of an error, it attempts to
    resume the change stream using the last known resume token.

    The MongoDB connection details (host, port, database name, and collection
    name) are retrieved from the `settings` object.

    Note:
        - The `directConnection=True` parameter is required for replica sets.
        - The pipeline is currently set to watch for all changes (empty filter).

    Raises:
        pymongo.errors.PyMongoError: If the ChangeStream encounters an
        unrecoverable error or the resume attempt fails to recreate the cursor.

    """
    client = motor.motor_asyncio.AsyncIOMotorClient(  # type: ignore  # noqa: PGH003
        f"mongodb://{settings.host}:{settings.port}",
        directConnection=True,  # this is required for replica sets
    )

    resume_token = None

    db: motor.motor_asyncio.AsyncIOMotorDatabase = client.get_database(
        settings.database_name
    )
    collection: motor.motor_asyncio.AsyncIOMotorCollection = db.get_collection(
        settings.collection_name
    )

    try:
        async with collection.watch() as stream:
            async for change in stream:
                logger.info("Change detected:")

                change: ChangeEvent

                match change["operationType"]:
                    case OperationType.INSERT:
                        logger.info("Operation type: insert")
                        logger.debug(change["fullDocument"])
                    case OperationType.UPDATE:
                        logger.info("Operation type: update")
                        logger.info(change["updateDescription"])
                    case OperationType.DELETE:
                        logger.info("Operation type: delete")
                        logger.info(change["documentKey"]["_id"])
                    case _:
                        logger.warning("Operation type not recognized")

                resume_token = stream.resume_token
    except pymongo.errors.PyMongoError:
        # The ChangeStream encountered an unrecoverable error or the
        # resume attempt failed to recreate the cursor.
        if resume_token is None:
            # There is no usable resume token because there was a
            # failure during ChangeStream initialization.
            logger.exception("...")
        else:
            # Use the interrupted ChangeStream's resume token to
            # create a new ChangeStream. The new stream will
            # continue from the last seen insert change without
            # missing any events.
            async with collection.watch(resume_after=resume_token) as stream:
                async for insert_change in stream:
                    logger.info(insert_change)


asyncio.run(watch_collection())

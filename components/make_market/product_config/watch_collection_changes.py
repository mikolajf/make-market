import asyncio

import motor.motor_asyncio
import pymongo.errors
from make_market.log.core import get_logger
from make_market.settings.models import Settings

logger = get_logger("__name__")

settings = Settings().config_database


async def watch_collection() -> None:
    client = motor.motor_asyncio.AsyncIOMotorClient(  # type: ignore  # noqa: PGH003
        f"mongodb://{settings.host}:{settings.port}",
        directConnection=True,  # this is required for replica sets
    )

    resume_token = None
    pipeline = [{"$match": {"operationType": "insert"}}]
    # pipeline = [{}]

    db = client.get_database("product")

    try:
        async with client.get_database("products").watch(pipeline) as stream:
            async for change in stream:
                logger.info(change)
                resume_token = stream.resume_token
    except pymongo.errors.PyMongoError:
        # The ChangeStream encountered an unrecoverable error or the
        # resume attempt failed to recreate the cursor.
        if resume_token is None:
            # There is no usable resume token because there was a
            # failure during ChangeStream initialization.
            logger.error("...")
        else:
            # Use the interrupted ChangeStream's resume token to
            # create a new ChangeStream. The new stream will
            # continue from the last seen insert change without
            # missing any events.
            async with client.get_database("products").watch(
                pipeline, resume_after=resume_token
            ) as stream:
                async for insert_change in stream:
                    print(insert_change)


# async def main() -> None:
#     while change_stream.alive:
#     change = await change_stream.try_next()
#     # Note that the ChangeStream's resume token may be updated
#     # even when no changes are returned.
#     print("Current resume token: %r" % (change_stream.resume_token,))
#     if change is not None:
#         print("Change document: %r" % (change,))
#         continue
#     # We end up here when there are no recent changes.
#     # Sleep for a while before trying again to avoid flooding
#     # the server with getMore requests when no changes are
#     # available.
#     await asyncio.sleep(10)

asyncio.run(watch_collection())

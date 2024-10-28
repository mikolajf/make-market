import asyncio
import random

from make_market.log.core import get_logger
from make_market.product_config import setup_database
from make_market.product_config.fetch import fetch_product_by_symbol
from make_market.product_config.schema import Listing, ProductConfig

logger = get_logger(__name__)


async def insert_one() -> None:
    """
    Inserts a new product into the database.

    This function creates an example product configuration. The product is then
    inserted into the database.

    Args:
        None

    Returns:
         None

    """
    logger.info("Inserting a new product")
    example_product = ProductConfig(
        symbol_name="EURUSD",
        decimal_places=5,
        listings=[
            Listing(provider_name="Provider1", subscription_symbol="EURUSD_1"),
            Listing(provider_name="Provider2", subscription_symbol="EURUSD_2"),
        ],
        enabled=True,
    )
    await example_product.insert()


async def edit_one() -> None:
    """
    Asynchronously edits a product by toggling its 'enabled' status.

    This function fetches a product with the symbol "EURUSD". If the product
    is found, it toggles the 'enabled' status of the product and saves the
    changes to the database. If the product is not found, it logs a warning.

    Returns:
        None

    """
    product_to_edit = await fetch_product_by_symbol("EURUSD")

    if product_to_edit:
        product_to_edit.enabled = not product_to_edit.enabled
        msg = f"Editing an existing product with id {product_to_edit.id}"
        logger.info(msg)

        await product_to_edit.save()
    else:
        logger.warning("No product found to edit")


async def delete_one() -> None:
    """
    Asynchronously deletes a product with the symbol "EURUSD" from the database.

    This function fetches a product by its symbol "EURUSD". If the product is found,
    it logs a message indicating the deletion of the product and proceeds to delete it.
    If no product is found, it logs a warning message.

    Returns:
        None

    """
    product_to_delete = await fetch_product_by_symbol("EURUSD")

    if not product_to_delete:
        logger.warning("No product found to delete")
        return

    msg = f"Deleting an existing product with id {product_to_delete.id}"
    logger.info(msg)
    await product_to_delete.delete()


async def main() -> None:
    """
    Main function to simulate changes in the product database.

    This function performs the following steps:
    1. Sets up the database by calling `setup_database()`.
    2. Inserts ten entries into the database by calling `insert_one()` in a loop.
    3. Enters an infinite loop where it randomly chooses one of the operations (`insert_one`, `edit_one`, `delete_one`)
        and executes it, followed by a 5-second delay.

    Returns:
         None

    """
    await setup_database()

    for _ in range(10):
        await insert_one()

    while True:
        # choose random operation from above three methods
        operation = random.choice([insert_one, edit_one, delete_one])  # noqa: S311
        await operation()
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())

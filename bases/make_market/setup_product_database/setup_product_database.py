import asyncio

from make_market.product_config import setup_database


async def main() -> None:
    """
    Main entry point for setting up the product database.

    This asynchronous function calls the setup_database function to initialize
    the product database.

    Returns:
        None

    """
    await setup_database()


if __name__ == "__main__":
    asyncio.run(main())

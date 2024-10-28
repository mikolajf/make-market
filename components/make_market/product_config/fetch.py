from make_market.product_config.schema import ProductConfig


async def fetch_all_products() -> list[ProductConfig]:
    """
    Fetches all product configurations.

    Returns:
        list[ProductConfig]: A list of all product configurations.

    """
    results = await ProductConfig.find_all().to_list()  # type: ignore  # noqa: PGH003

    return results

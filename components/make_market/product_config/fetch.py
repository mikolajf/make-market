from make_market.product_config.schema import ProductConfig


async def fetch_all_products() -> list[ProductConfig]:
    """
    Fetches all product configurations.

    Returns:
        list[ProductConfig]: A list of all product configurations.

    """
    return await ProductConfig.find_all().to_list()  # type: ignore  # noqa: PGH003


async def fetch_product_by_symbol(symbol_name: str) -> ProductConfig:
    """
    Fetches a product configuration by symbol name.

    Args:
        symbol_name (str): The symbol name of the product.

    Returns:
        ProductConfig: The product configuration matching the symbol name.

    """
    return await ProductConfig.find_one(ProductConfig.symbol_name == symbol_name)  # type: ignore  # noqa: PGH003

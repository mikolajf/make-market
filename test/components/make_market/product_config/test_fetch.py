import pytest
from beanie import init_beanie  # type: ignore  # noqa: PGH003
from make_market.product_config.fetch import fetch_all_products
from make_market.product_config.schema import Listing, ProductConfig
from mongomock_motor import AsyncMongoMockClient  # type: ignore  # noqa: PGH003


@pytest.fixture(autouse=True)
async def setup_mongo_mock() -> None:
    client = AsyncMongoMockClient()  # type: ignore  # noqa: PGH003
    await init_beanie(
        document_models=[ProductConfig],
        database=client.get_database(name="test_db"),  # type: ignore  # noqa: PGH003
    )

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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fetch_all_products_with_mocker() -> None:
    # Call the function
    result = await fetch_all_products()

    assert len(result) == 1
    assert result[0].symbol_name == "EURUSD"

from beanie import Document
from pydantic import BaseModel, Field


class Listing(BaseModel):
    """
    Listing model representing a product listing configuration.
    """

    provider_name: str
    subscription_symbol: str
    enabled: bool = Field(default=True)


class ProductConfig(Document):
    """
    ProductConfig is a document model representing the configuration of a product in the market.
    """

    symbol_name: str
    decimal_places: int
    listings: list[Listing]
    enabled: bool = Field(default=True)

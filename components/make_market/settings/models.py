from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigDatabaseSettings(BaseModel):
    """
    ConfigDatabaseSettings is a Pydantic model that holds the configuration settings for a database connection.

    Attributes:
        host (str): The hostname or IP address of the database server.
        port (int): The port number on which the database server is listening.
        username (str): The username to use for authenticating with the database.
        password (str): The password to use for authenticating with the database.

    """

    host: str = "localhost"
    port: int = 5432
    username: str = "postgres"
    password: str = "password"


class QuestDatabaseSettings(BaseModel):
    """
    QuestDatabaseSettings is a configuration model for database settings.

    Attributes:
        host (str): The hostname or IP address of the database server.
        web_console_port (int): The port number for the web console.
        influxdb_port (int): The port number for the InfluxDB service.
        postgres_port (int): The port number for the PostgreSQL service.
        min_health_port (int): The port number for the minimum health check service.

    """

    host: str = "localhost"
    web_console_port: int = 9000
    influxdb_port: int = 9009
    postgres_port: int = 8812
    min_health_port: int = 9003


class VendorWebscoketServerSettings(BaseModel):
    """
    VendorWebscoketServerSettings defines the settings for the vendor websocket server.

    Attributes:
        THROTTHLE_INTERVAL (int): The interval in seconds for throttling the websocket server.

    """

    THROTTHLE_INTERVAL: int = 1
    URL: str = "ws://localhost:8765"


class Settings(BaseSettings, case_sensitive=False):
    """
    Settings class for application configuration.

    Attributes:
        config_database (ConfigDatabaseSettings): Configuration settings for the database.
        quest (QuestDatabaseSettings): Configuration settings for the quest database.

    """

    model_config = SettingsConfigDict(
        env_prefix="mm_",
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
    )

    config_database: ConfigDatabaseSettings = ConfigDatabaseSettings()
    quest: QuestDatabaseSettings = QuestDatabaseSettings()
    vendor_websocket: VendorWebscoketServerSettings = VendorWebscoketServerSettings()

    dummy_setting: str = "dummy"

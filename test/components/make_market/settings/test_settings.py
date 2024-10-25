import pytest
from make_market.settings import Settings
from make_market.settings.models import (
    ConfigDatabaseSettings,
    QuestDatabaseSettings,
    VendorWebscoketServerSettings,
)
from pydantic import ValidationError


def test_default_settings():
    settings = Settings()
    assert settings.config_database.host == "localhost"
    assert settings.config_database.port == 5432
    assert settings.config_database.username == "postgres"
    assert settings.config_database.password == "password"  # noqa: S105
    assert settings.quest.host == "localhost"
    assert settings.quest.web_console_port == 9000
    assert settings.quest.influxdb_port == 9009
    assert settings.quest.postgres_port == 8812
    assert settings.quest.min_health_port == 9003
    assert settings.vendor_websocket.THROTTHLE_INTERVAL == 1
    assert settings.dummy_setting == "dummy"


def test_env_variable_overrides(monkeypatch):
    monkeypatch.setenv("MM_CONFIG_DATABASE__HOST", "127.0.0.1")
    monkeypatch.setenv("MM_CONFIG_DATABASE__PORT", "3306")
    monkeypatch.setenv("MM_CONFIG_DATABASE__USERNAME", "admin")
    monkeypatch.setenv("MM_CONFIG_DATABASE__PASSWORD", "adminpass")
    monkeypatch.setenv("MM_QUEST__HOST", "127.0.0.2")
    monkeypatch.setenv("MM_QUEST__WEB_CONSOLE_PORT", "8000")
    monkeypatch.setenv("MM_QUEST__INFLUXDB_PORT", "8009")
    monkeypatch.setenv("MM_QUEST__POSTGRES_PORT", "7812")
    monkeypatch.setenv("MM_QUEST__MIN_HEALTH_PORT", "8003")
    monkeypatch.setenv("MM_VENDOR_WEBSOCKET__THROTTHLE_INTERVAL", "2")
    monkeypatch.setenv("MM_DUMMY_SETTING", "new_dummy")

    settings = Settings()
    assert settings.config_database.host == "127.0.0.1"
    assert settings.config_database.port == 3306
    assert settings.config_database.username == "admin"
    assert settings.config_database.password == "adminpass"  # noqa: S105
    assert settings.quest.host == "127.0.0.2"
    assert settings.quest.web_console_port == 8000
    assert settings.quest.influxdb_port == 8009
    assert settings.quest.postgres_port == 7812
    assert settings.quest.min_health_port == 8003
    assert settings.vendor_websocket.THROTTHLE_INTERVAL == 2
    assert settings.dummy_setting == "new_dummy"


def test_invalid_settings():
    with pytest.raises(ValidationError):
        ConfigDatabaseSettings(port="invalid_port")

    with pytest.raises(ValidationError):
        QuestDatabaseSettings(web_console_port="invalid_port")

    with pytest.raises(ValidationError):
        VendorWebscoketServerSettings(THROTTHLE_INTERVAL="invalid_interval")

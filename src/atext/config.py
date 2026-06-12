from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for atext."""

    model_config = SettingsConfigDict(env_prefix="ATEXT_", env_file=".env", extra="ignore")

    database_url: str = Field(default="postgresql://localhost/atext")
    awid_registry_url: str = Field(default="https://api.awid.ai")
    auth_cache_ttl_seconds: int = Field(default=600, ge=1)
    timestamp_skew_seconds: int = Field(default=300, ge=1)
    public_origin: str = Field(default="http://127.0.0.1:8765")


def get_settings() -> Settings:
    return Settings()

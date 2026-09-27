"""Configuration loading: TOML file plus environment overrides."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from forge.models.config import ForgeConfig


class _Env(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FORGE_", env_file=".env", extra="ignore")

    proxy_uri: str | None = None
    captcha_key: str | None = None
    mail_api_key: str | None = None


def load_config(path: Path) -> ForgeConfig:
    """Load a `ForgeConfig` from TOML, overlaying environment secrets."""
    if path.exists():
        cfg = ForgeConfig.from_toml(path)
    else:
        cfg = ForgeConfig()
    env = _Env()
    updates: dict[str, object] = {}
    if env.proxy_uri:
        updates["default_proxy_uri"] = env.proxy_uri
    if env.captcha_key:
        updates["captcha_api_key"] = env.captcha_key
    if env.mail_api_key:
        updates["mail_api_key"] = env.mail_api_key
    return cfg.model_copy(update=updates) if updates else cfg
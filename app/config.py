"""Configuration classes for Dev / Prod / Test environments."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_SECRET = "dev-secret-key-change-in-production"


class Config:
    """Base configuration."""

    SECRET_KEY: str = os.getenv("SECRET_KEY", _DEFAULT_SECRET)
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")

    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "output")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")

    # LLM defaults
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "120"))
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "2"))

    # Provider API keys (server-side)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    def __init__(self) -> None:
        if self.SECRET_KEY == _DEFAULT_SECRET:
            raise RuntimeError(
                "ProductionConfig: SECRET_KEY must be changed from the default value."
            )


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SECRET_KEY = "test-secret-key"


def get_config() -> Config:
    env = os.getenv("FLASK_ENV", "development").lower()
    mapping: dict[str, type[Config]] = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }
    cfg_class = mapping.get(env, DevelopmentConfig)
    return cfg_class()

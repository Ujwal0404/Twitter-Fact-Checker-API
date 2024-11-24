from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv
from .utils.logging import get_logger

load_dotenv()
logger = get_logger("fact_checker.config")

class Settings(BaseSettings):
    APP_NAME: str = "Fact Checker API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    GROQ_API_KEY: str
    TWITTER_BEARER_TOKEN: str
    CACHE_TTL: int = 86400
    MAX_WORKERS: int = 3

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    logger.info("Loading application settings")
    return Settings()
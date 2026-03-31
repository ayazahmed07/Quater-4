import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Configuration settings for the PSX AI Agent.
    Values are automatically loaded from environment variables and .env file.
    """
    # Whapi.cloud API Configuration
    whapi_api_url: str = "https://gate.whapi.cloud"
    whapi_api_token: str
    whapi_recipient_number: str

    # Scraping Configuration
    news_url: str = "https://jang.com.pk/category/latest-news"
    scrape_interval_seconds: int = 300

    # Storage and Logging
    database_file: str = "storage/database.json"
    log_file: str = "logs/psx_agent.log"

    # Tell pydantic to use the .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Create a singleton settings object
try:
    settings = Settings()
except Exception as e:
    # This might fail during setup if .env is missing. 
    # That's fine for now, we'll provide instructions.
    settings = None
    print(f"Warning: Could not load settings from .env: {e}")

from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """
    Central configuration for the application.
    Values are loaded strictly from environment variables.
    """

    # ===============================
    # Application Settings
    # ===============================
    APP_NAME: str = "AIRMAN AI Dispatch System"
    ENVIRONMENT: str = "development"

    # ===============================
    # Database Settings (NO DEFAULT!)
    # ===============================
    DATABASE_URL: str

    # ===============================
    # Weather Service Settings
    # ===============================
    WEATHER_CACHE_TTL: int = 600

    # ===============================
    # Dispatch Settings
    # ===============================
    DEFAULT_BASE_ICAO: str = "VOBG"

    # ===============================
    # Evaluation Settings
    # ===============================
    SCENARIO_FOLDER: str = "evaluation_scenarios"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()

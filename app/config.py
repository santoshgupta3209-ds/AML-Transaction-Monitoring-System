from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # ==============================
    # Application
    # ==============================

    APP_NAME: str = "AI-Based AML Transaction Monitoring System"

    ENVIRONMENT: str = "development"


    # ==============================
    # Database
    # ==============================

    DATABASE_URL: str


    # ==============================
    # JWT Security
    # ==============================

    SECRET_KEY: str

    JWT_SECRET: str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


    # ==============================
    # Machine Learning
    # ==============================

    MODEL_PATH: str = "app/ml/aml_model.pkl"

    ML_THRESHOLD: float = 0.70


    # ==============================
    # Risk Levels
    # ==============================

    LOW_THRESHOLD: float = 0.40

    HIGH_THRESHOLD: float = 0.70


    # ==============================
    # Environment File
    # ==============================

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    raw_data_path: Path = PROJECT_ROOT / "data" / "raw"

    warehouse_path: Path = (
        PROJECT_ROOT / "data" / "warehouse" / "customer_analytics.duckdb"
    )

    sql_path: Path = PROJECT_ROOT / "ingestion" / "sql"

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()

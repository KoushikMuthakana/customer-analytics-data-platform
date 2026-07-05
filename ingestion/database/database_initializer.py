from ingestion.config.settings import settings
from ingestion.database.duckdb_client import DuckDBClient


class DatabaseInitializer:
    def __init__(self, db: DuckDBClient):

        self.db = db

    def initialize(self) -> None:
        """
        Bootstrap the database.
        """

        self.db.execute_script(settings.sql_path / "init.sql")

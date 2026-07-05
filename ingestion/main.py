import logging

from ingestion.config.settings import settings
from ingestion.database.duckdb_client import DuckDBClient
from ingestion.models.datasets import DATASETS
from ingestion.pipelines.service import IngestionService

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)


def main() -> None:

    with DuckDBClient() as db:
        service = IngestionService(db)

        service.run(*DATASETS)


if __name__ == "__main__":
    main()

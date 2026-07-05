import logging
import time

from ingestion.config.settings import settings
from ingestion.database.database_initializer import DatabaseInitializer
from ingestion.database.duckdb_client import DuckDBClient
from ingestion.models.datasets import Dataset
from ingestion.pipelines.checkpoint import Checkpoint
from ingestion.pipelines.writer import Writer

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, db: DuckDBClient):

        self.db = db
        self.writer = Writer(db)
        self.initializer = DatabaseInitializer(db)
        self.checkpoint = Checkpoint(db)

    def run(self, *datasets: Dataset) -> None:
        """
        Execute ingestion for one or more datasets.
        """

        self.db.execute_script(settings.sql_path / "init.sql")

        for dataset in datasets:
            self._ingest_dataset(dataset)

        logger.info("Pipeline completed successfully.")

    def _ingest_dataset(self, dataset: Dataset) -> None:

        source_file = settings.raw_data_path / dataset.source_file

        logger.info(f"Processing '{dataset.source_file}'")

        if self.checkpoint.is_completed(dataset.source_file):
            logger.info(f"Skipping '{dataset.source_file}' (already processed)")

            return

        cleanup_previous_load = self.checkpoint.is_failed(dataset.source_file)

        self.checkpoint.mark_running(dataset.source_file)

        start = time.perf_counter()

        try:
            with self.db.transaction():
                rows_loaded = self.writer.ingest(
                    dataset=dataset,
                    source_file=source_file,
                    cleanup_previous_load=cleanup_previous_load,
                )

                self.checkpoint.mark_completed(
                    filename=dataset.source_file,
                    rows_loaded=rows_loaded,
                )

            elapsed = time.perf_counter() - start

            logger.info(
                f"Loaded {rows_loaded:,} rows into "
                f"bronze.{dataset.table} "
                f"in {elapsed:.2f}s"
            )

        except Exception:
            self.checkpoint.mark_failed(dataset.source_file)

            logger.exception(f"Failed processing '{dataset.source_file}'")

            raise

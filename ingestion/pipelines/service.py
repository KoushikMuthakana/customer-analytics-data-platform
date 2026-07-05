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
        all_files = [str(file.name) for file in sorted(settings.raw_data_path.glob("*.json")) if file.name.startswith(dataset.source_file)
]       
        logger.info(f"Processing all these file: '{all_files}'")
        
        for file in all_files:
            source_file_path = settings.raw_data_path / file
            logger.info(f"Processing '{file}'")

            if self.checkpoint.is_completed(file):
                logger.info(f"Skipping '{file}' (already processed)")

                return

            cleanup_previous_load = self.checkpoint.is_failed(file)

            self.checkpoint.mark_running(file)

            start = time.perf_counter()

            try:
                with self.db.transaction():
                    rows_loaded = self.writer.ingest(
                        dataset=dataset,
                        source_file=source_file_path,
                        cleanup_previous_load=cleanup_previous_load,
                    )

                    self.checkpoint.mark_completed(
                        filename=file,
                        rows_loaded=rows_loaded,
                    )

                elapsed = time.perf_counter() - start

                logger.info(
                    f"Loaded {rows_loaded:,} rows into "
                    f"bronze.{dataset.table} "
                    f"in {elapsed:.2f}s"
                )

            except Exception:
                self.checkpoint.mark_failed(file)

                logger.exception(f"Failed processing '{file}'")

                raise

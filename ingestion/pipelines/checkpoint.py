from datetime import datetime

from ingestion.config.constants import (
    COMPLETED,
    FAILED,
    INGESTION_RUNS_TABLE,
    METADATA_SCHEMA,
    RUNNING,
)
from ingestion.database.duckdb_client import DuckDBClient


class Checkpoint:
    def __init__(self, db: DuckDBClient):
        self.db = db

    def is_completed(self, filename: str) -> bool:

        result = self.db.scalar(
            f"""
            SELECT 1

            FROM {METADATA_SCHEMA}.{INGESTION_RUNS_TABLE}

            WHERE filename = ?
              AND status = ?
            """,
            [
                filename,
                COMPLETED,
            ],
        )

        return result is not None

    def is_failed(self, filename: str) -> bool:

        result = self.db.scalar(
            f"""
            SELECT 1

            FROM {METADATA_SCHEMA}.{INGESTION_RUNS_TABLE}

            WHERE filename = ?
              AND status = ?
            """,
            [
                filename,
                FAILED,
            ],
        )

        return result is not None

    def mark_running(self, filename: str) -> None:

        self.db.execute(
            f"""
            INSERT OR REPLACE INTO
            {METADATA_SCHEMA}.{INGESTION_RUNS_TABLE}

            (
                filename,
                status,
                started_at,
                completed_at,
                rows_loaded
            )

            VALUES
            (
                ?,
                ?,
                ?,
                NULL,
                NULL
            )
            """,
            [
                filename,
                RUNNING,
                datetime.now(),
            ],
        )

    def mark_completed(
        self,
        filename: str,
        rows_loaded: int,
    ) -> None:

        self.db.execute(
            f"""
            UPDATE {METADATA_SCHEMA}.{INGESTION_RUNS_TABLE}

            SET

                status = ?,

                completed_at = ?,

                rows_loaded = ?

            WHERE filename = ?
            """,
            [
                COMPLETED,
                datetime.now(),
                rows_loaded,
                filename,
            ],
        )

    def mark_failed(self, filename: str) -> None:

        self.db.execute(
            f"""
            UPDATE {METADATA_SCHEMA}.{INGESTION_RUNS_TABLE}

            SET status = ?

            WHERE filename = ?
            """,
            [
                FAILED,
                filename,
            ],
        )

    def reset(self) -> None:

        self.db.execute(
            f"""
            DELETE

            FROM {METADATA_SCHEMA}.{INGESTION_RUNS_TABLE}
            """
        )

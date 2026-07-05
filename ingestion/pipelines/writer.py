from pathlib import Path

from ingestion.config.constants import BRONZE_SCHEMA
from ingestion.database.duckdb_client import DuckDBClient
from ingestion.models.datasets import Dataset


class Writer:
    def __init__(self, db: DuckDBClient):
        self.db = db

    def ingest(
        self, dataset: Dataset, source_file: Path, cleanup_previous_load: bool = False
    ) -> int:

        if not source_file.exists():
            raise FileNotFoundError(source_file)

        if not self.db.table_exists(
            BRONZE_SCHEMA,
            dataset.table,
        ):
            self._create_table(dataset)
        if cleanup_previous_load:
            self._cleanup(dataset, source_file.name)

        self._load(dataset, source_file)

        return self._count(dataset, source_file.name)

    def _create_table(
        self,
        dataset: Dataset,
    ) -> None:

        columns = []

        for column in dataset.columns:
            columns.append(f"{column.name} {column.datatype}")

        columns.extend(
            [
                "source_file VARCHAR",
                "ingestion_timestamp TIMESTAMP",
            ]
        )

        sql = f"""
        CREATE TABLE {BRONZE_SCHEMA}.{dataset.table}
        (
            {", ".join(columns)}
        )
        """

        self.db.execute(sql)

    def _cleanup(
        self,
        dataset: Dataset,
        filename: str,
    ) -> None:

        sql = f"""
        DELETE

        FROM {BRONZE_SCHEMA}.{dataset.table}

        WHERE source_file = ?
        """

        self.db.execute(
            sql,
            [
                filename,
            ],
        )

    def _load(
        self,
        dataset: Dataset,
        source_file: Path,
    ) -> None:

        destination_columns = []

        source_columns = []

        for column in dataset.columns:
            destination_columns.append(column.name)

            source_columns.append(
                self._cast(
                    column.name,
                    column.datatype,
                )
            )

        destination_columns.extend(
            [
                "source_file",
                "ingestion_timestamp",
            ]
        )

        source_columns.extend(
            [
                "? AS source_file",
                "CURRENT_TIMESTAMP AS ingestion_timestamp",
            ]
        )

        sql = f"""
        INSERT INTO {BRONZE_SCHEMA}.{dataset.table}
        (
            {",".join(destination_columns)}
        )

        SELECT

        {",".join(source_columns)}

        FROM read_ndjson_auto(?)
        """

        self.db.execute(
            sql,
            [
                source_file.name,
                str(source_file),
            ],
        )

    def _count(
        self,
        dataset: Dataset,
        filename: str,
    ) -> int:

        sql = f"""
        SELECT COUNT(*)

        FROM {BRONZE_SCHEMA}.{dataset.table}

        WHERE source_file = ?
        """

        return self.db.scalar(
            sql,
            [
                filename,
            ],
        )

    def _cast(
        self,
        column: str,
        datatype: str,
    ) -> str:

        if datatype == "JSON":
            return f"TRY_CAST({column} AS JSON) AS {column}"

        return f"TRY_CAST({column} AS {datatype}) AS {column}"

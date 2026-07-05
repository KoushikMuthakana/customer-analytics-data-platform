from contextlib import contextmanager
from pathlib import Path

import duckdb

from ingestion.config.settings import settings


class DuckDBClient:
    def __init__(self) -> None:
        try:
            self.connection = duckdb.connect(database=str(settings.warehouse_path))
        except duckdb.IOException as err:
            raise RuntimeError(
                "Unable to open DuckDB databaase..."
                " Another application may already have it open. "
                "Please close the connection and try again."
            ) from err

    def execute(self, sql: str, params: list | None = None) -> None:

        if params:
            self.connection.execute(sql, params)
        else:
            self.connection.execute(sql)

    def fetch_one(
        self,
        sql: str,
        params: list | None = None,
    ):

        if params:
            return self.connection.execute(sql, params).fetchone()

        return self.connection.execute(sql).fetchone()

    def fetch_all(
        self,
        sql: str,
        params: list | None = None,
    ):

        if params:
            return self.connection.execute(sql, params).fetchall()

        return self.connection.execute(sql).fetchall()

    def fetch_df(
        self,
        sql: str,
        params: list | None = None,
    ):

        if params:
            return self.connection.execute(sql, params).fetchdf()

        return self.connection.execute(sql).fetchdf()

    def execute_script(self, script_path: Path) -> None:

        self.connection.execute(script_path.read_text())

    def table_exists(
        self,
        schema: str,
        table: str,
    ) -> bool:

        result = self.fetch_one(
            """
            SELECT 1

            FROM information_schema.tables

            WHERE table_schema = ?
              AND table_name = ?
            """,
            [
                schema,
                table,
            ],
        )

        return result is not None

    @contextmanager
    def transaction(self):

        try:
            self.connection.begin()

            yield

            self.connection.commit()

        except Exception:
            self.connection.rollback()

            raise

    def scalar(
        self,
        sql: str,
        params: list | None = None,
    ):

        result = self.fetch_one(sql, params)

        return None if result is None else result[0]

    def close(self):

        self.connection.close()

    def __enter__(self):

        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ):

        self.close()

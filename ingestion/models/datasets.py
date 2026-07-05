from dataclasses import dataclass


@dataclass(frozen=True)
class Column:
    name: str
    datatype: str


@dataclass(frozen=True)
class Dataset:
    table: str
    source_file: str
    columns: list[Column]


CUSTOMER_SESSIONS = Dataset(
    table="customer_sessions",
    source_file="customer_sessions",
    columns=[
        Column("id", "BIGINT"),
        Column("firstsession", "BOOLEAN"),
        Column("applicationid", "INTEGER"),
        Column("profileid", "BIGINT"),
        Column("profileintegrationid", "VARCHAR"),
        Column("store_integration_id", "INTEGER"),
        Column("loyaltycards", "JSON"),
        Column("created", "TIMESTAMP"),
        Column("state", "VARCHAR"),
        Column("cartitems", "JSON"),
        Column("additional_costs", "JSON"),
        Column("discounts", "JSON"),
        Column("attributes", "JSON"),
        Column("updated", "TIMESTAMP"),
        Column("closedat", "TIMESTAMP"),
        Column("total_float", "DOUBLE"),
        Column("__ts_ms", "BIGINT"),
        Column("__op", "VARCHAR"),
        Column("__deleted", "BOOLEAN"),
    ],
)


PROFILES = Dataset(
    table="profiles",
    source_file="profiles",
    columns=[
        Column("id", "BIGINT"),
        Column("attributes", "JSON"),
        Column("sandbox", "BOOLEAN"),
        Column("__ts_ms", "BIGINT"),
        Column("__op", "VARCHAR"),
        Column("__deleted", "BOOLEAN"),
    ],
)


DATASETS = [
    CUSTOMER_SESSIONS,
    PROFILES,
]

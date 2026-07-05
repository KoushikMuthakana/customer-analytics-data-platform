CREATE SCHEMA IF NOT EXISTS bronze;

CREATE SCHEMA IF NOT EXISTS metadata;

CREATE TABLE IF NOT EXISTS metadata.ingestion_runs (

    filename VARCHAR PRIMARY KEY,

    status VARCHAR NOT NULL,

    started_at TIMESTAMP,

    completed_at TIMESTAMP,

    rows_loaded BIGINT

);
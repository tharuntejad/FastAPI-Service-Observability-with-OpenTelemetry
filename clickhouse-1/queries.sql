/*
    ClickHouse Queries for OpenTelemetry Data

    These queries can be executed using ClickHouse clients such as:
    - `clickhouse-client`
    - Grafana's ClickHouse SQL editor
    - ClickHouse Web UI(if you are using clickhouse-cloud)

    The `default` database exists by default on the ClickHouse server.
    The OpenTelemetry (OTel) collector automatically creates the necessary tables
    and inserts telemetry data into them.

    The main tables include:
    - `otel_logs`       : Stores log entries.
    - `otel_traces`     : Stores trace data.
    - `otel_metrics_sum`: Stores aggregated metric data.
    - `otel_metrics_gauge`: Stores gauge metric data.
    - `otel_metrics_histogram`: Stores histogram metric data.
    - `otel_metrics_exponential_histogram`: Stores exponential histogram metric data.
*/



-- List all available databases in ClickHouse
SHOW DATABASES;

-- Switch to the "default" database
USE default;

-- List all tables in the "default" database
SHOW TABLES;

-- Fetch the first 10 log entries from the OpenTelemetry logs table
SELECT *
FROM otel_logs
LIMIT 10;

-- Fetch the first 10 trace entries from the OpenTelemetry traces table
SELECT *
FROM otel_traces
LIMIT 10;

-- Fetch the first 10 metric summaries from the OpenTelemetry metrics table
SELECT *
FROM otel_metrics_sum
LIMIT 10;

/*
 * Retention Policies for ClickHouse Tables
 *
 * The volume of telemetry data (logs, metrics, and traces) can grow rapidly, leading to excessive storage usage.
 * To manage storage effectively, we apply retention policies using ClickHouse's `TTL` (Time-To-Live) feature.
 * This ensures logs, metrics, and traces are automatically removed after a defined period based on their importance.
 *
 * The following script modifies TTL for different telemetry tables, ensuring:
 * - Logs are retained based on severity levels.
 * - Traces are retained based on their status codes.
 * - Metrics are retained for a fixed duration.
 */

-- Use the default database (ensure you're operating in the correct context)
USE default;

-- ========================
-- Retention Policy for Logs
-- ========================
ALTER TABLE otel_logs
MODIFY TTL
    toDateTime(Timestamp) + INTERVAL 1 MONTH WHERE SeverityText = 'INFO',    -- Retain INFO logs for 1 month
    toDateTime(Timestamp) + INTERVAL 2 MONTH WHERE SeverityText = 'WARNING', -- Retain WARNING logs for 2 months
    toDateTime(Timestamp) + INTERVAL 3 MONTH WHERE SeverityText = 'ERROR';   -- Retain ERROR logs for 3 months

-- =========================
-- Retention Policy for Traces
-- =========================
ALTER TABLE otel_traces
MODIFY TTL
    toDateTime(Timestamp) + INTERVAL 1 MONTH WHERE StatusCode = 'Ok',    -- Retain successful spans for 1 month
    toDateTime(Timestamp) + INTERVAL 2 MONTH WHERE StatusCode = 'Error', -- Retain error spans for 2 months
    toDateTime(Timestamp) + INTERVAL 1 MONTH WHERE StatusCode = 'Unset'; -- Retain unset status spans for 1 month

-- =========================
-- Retention Policy for Metrics
-- =========================
-- Metrics are usually stored for a fixed duration, so we apply a standard TTL of 1 month for all relevant tables.

ALTER TABLE otel_metrics_sum
MODIFY TTL toDateTime(TimeUnix) + INTERVAL 1 MONTH;  -- Retain summed metrics for 1 month

ALTER TABLE otel_metrics_histogram
MODIFY TTL toDateTime(TimeUnix) + INTERVAL 1 MONTH;  -- Retain histogram metrics for 1 month

ALTER TABLE otel_metrics_guage
MODIFY TTL toDateTime(TimeUnix) + INTERVAL 1 MONTH;  -- Retain gauge metrics for 1 month

ALTER TABLE otel_metrics_histogram
MODIFY TTL toDateTime(TimeUnix) + INTERVAL 1 MONTH;  -- Retain histogram metrics for 1 month

ALTER TABLE otel_metrics_exponential_histogram
MODIFY TTL toDateTime(TimeUnix) + INTERVAL 1 MONTH;  -- Retain exponential histogram metrics for 1 month

/*
 * Summary:
 * - Logs have different retention periods based on severity.
 * - Traces have different retention periods based on status codes.
 * - Metrics have a uniform 1-month retention policy.

You can customize the retention periods using various time units such as `minute`, `hour`, `day`, `week`, `month``, or `year`.
 *
 * This structured approach ensures optimal storage management while preserving critical telemetry data.
 */

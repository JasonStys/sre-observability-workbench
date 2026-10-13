# Evidence, SLI and alert contracts

## Versioned client attempts

JSONL fields are exactly `schema`, `id`, `at_ms`, `duration_us`, `status`, `trace_id`, `span_id`. Schema 1 uses UTC completion milliseconds and monotonic elapsed microseconds. IDs are unique positive integers; trace/span identifiers are nonzero lower-case hex (32/16 characters). HTTP status 0 means connection/timeout/cap failure. Status 100–599 is accepted; only 2xx is successful. Duplicate keys, IDs, blank lines, oversized input, extra fields and malformed measurements fail validation. Files are parsed as data, never executed.

Analysis window: **(as_of_ms − window_ms, as_of_ms]**. The default reporting window is 30 days, but the report includes observed span; a subsecond drill is not 30 days of measured uptime. `expected_events` is an operator assertion of the number of attempts in the reporting window. Missing, extra or future records make the alert `INSUFFICIENT_DATA`. A matching count is `COMPLETE_ASSERTED`, not independently authenticated provenance. Zero/sparse traffic still cannot produce CLEAR.

## Two independent SLOs

Default objective: 999,000 parts per million (99.9%). Latency threshold: 50,000 µs. Availability good = 2xx. Latency good = 2xx **and** duration ≤ threshold. Fast failures are bad for both. Failed and timed-out attempts remain in percentile/SLI denominators. These are request-based, not uptime-based or CPU-efficiency objectives.

For N requests, B bad requests, target T in parts per million:

```text
allowed_bad = N × (1,000,000 − T) / 1,000,000
remaining = allowed_bad − B     (negative is intentionally possible)
burn = B / allowed_bad
```

Fractions govern comparisons; floating output is only presentation. Zero attempts has no ratio/burn; a 100% target is rejected to prevent division by zero. Raw p50/p95/p99 use nearest rank, including unsuccessful attempts. Grafana uses Prometheus histogram interpolation: its p95 is an estimate with different data/timing than raw client p95 and must not be represented as identical.

## Multiwindow pages

Fast pair: both 1 h and 5 min burns strictly exceed 14.4. Slow pair: both 6 h and 30 min burns strictly exceed 6. Either active pair pages. Each offline pair requires 20 observations in both windows by default. If no pair pages and either is under volume, the result is insufficient data. Equality with a threshold does not page. Recovery of current requests does not instantly erase historical budget burn.

Checked-in PromQL implements these fixed default thresholds, gates pages on at least 20 estimated requests in 5 min, and separately emits `SLOInsufficientData` for low/missing volume and `TelemetryMissing` for unavailable/absent scrapes. `rate`/`increase` handle counter resets and extrapolate between scrapes; offline integer counts do not. Prometheus `up` is exporter scrape health, not the user request SLI. NaN or an empty alert table is not a health assertion. No Alertmanager delivery, deduplication or page acknowledgement system is provided.

Traceparent v00 accepts valid nonzero IDs and flags 00/01. Local demo spans intentionally sample every request even if incoming flags are 00; this supports exhaustive synthetic trace correlation, not a production sampling policy. Baggage/tracestate and raw user/URL/header/exception data are discarded. An attacker able to call localhost may forge correlation IDs; IDs are not authentication.

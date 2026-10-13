# Architecture and ADR-001: a bounded native observability lab

Status: accepted. Date: 2026-10-13. Portfolio author: Jason Stys. Implementation review: author-led, not independent approval.

## Requirements and constraints

Demonstrate real metrics/logs/traces, request-based SLOs, fault/recovery reasoning and CI verification without touching an existing fleet, Docker Desktop, cloud account or private customer data. First success should require only Python/Node dependencies. Local resource use and evidence must be bounded. Tests must expose missing evidence and privacy violations, not just happy-path output.

```text
TypeScript bounded client ─HTTP + traceparent→ Python gateway ─HTTP + traceparent→ worker
       │ events + SDK spans                     │ metrics/logs/spans             │
       └───────────→ Python SLO analyzer → HTML / JSON / indexed SQLite ←────────┘
                            Prometheus ← scrape gateway/worker → Grafana panels
```

Only the **client attempt stream** defines offline request SLIs. Adding gateway and worker logs to that denominator would double-count the same operation. Prometheus measures completed gateway work, not clients that failed to connect. Both viewpoints are useful; neither is substituted for the other.

## Decision and alternatives

Python owns service instrumentation, exact rational SLO arithmetic, validation and SQLite/reporting: its standard library keeps these boundaries inspectable. TypeScript owns bounded asynchronous traffic and typed Node/OpenTelemetry integration: concurrent I/O is explicit without threads. SQL expresses indexed evidence queries; Bash orchestrates portable gates without evaluating input. Prometheus/Grafana are existing observability tools, not reimplemented chart/render engines.

Compared with a Docker-only microservice stack, this design has a simpler cross-platform start and leaves this PC's Docker unchanged, but vendor dashboard runtime validation is Linux CI-only. Compared with fixture-only analysis, actual HTTP/SDK/scrape tests cost seconds of runtime but expose propagation, metric denominator, lifecycle and scrape-loss errors. A hosted SaaS would add authentication/storage/TLS/tenancy obligations inappropriate for this local lab; none are claimed here.

No arbitrary plugin code, external exporter, production fault control or dynamic remote target discovery is allowed. Every attempt has a deadline; the batch is finite. The local services expose only fixed endpoints, with at most 16 concurrent handlers each. A 1,000-attempt client batch has at most eight asynchronous workers. Evidence loading caps at 8 MiB and 10,000 attempts. Each service span/log stream caps at 10,000 records; long-lived interactive use must restart with new evidence before the cap.

## Performance and growth

Core assessment scans a constant number of windows in O(N), uses O(N log N) sorting for nearest-rank duration percentiles and O(N) memory. Drill correlation indexes spans/logs by trace ID for O(N) matching. SQLite's `(at_ms,status)` index supports time/status filtering without SQL interpolation. Benchmarks measure the bounded analyzer, **not** production service capacity or a mathematical complexity proof.

At larger scale, revisit streaming quantiles, retention/drop indicators, request admission, authenticated trace context, secure collector transports, persistent queues, recording-rule tenancy, a trace backend, alert delivery/inhibition and production isolation. The deliberate offline exact arithmetic and PromQL extrapolation need separate contracts. Do not expand the fault/target boundary without a new threat model and authorization.

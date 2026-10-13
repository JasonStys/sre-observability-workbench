# Primary sources and implementation rationale

Reviewed 2026-10-13. Sources are technical references, not authorization to run on external systems.

- [Google SRE: alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) informed the 1h/5m 14.4 and 6h/30m 6 burn pairs, strict comparison, recovery windows and low-traffic caveats. This lab implements page-level pairs, not a complete escalation/inhibition system.
- [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/) informed counters, bounded labels and separation of business requests from health/scrape traffic.
- [Prometheus metric types](https://prometheus.io/docs/concepts/metric_types/) informed histogram buckets and explicit separation between histogram estimates and raw nearest-rank percentiles.
- [Native Prometheus rule unit testing](https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/) provides the actual rule-test format and missing/reset series semantics; native execution verifies our fixtures rather than a homemade PromQL substitute.
- [Python OpenTelemetry instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/) and [JavaScript instrumentation](https://opentelemetry.io/docs/languages/js/instrumentation/) informed service-owned SDK providers, spans/statuses and client integration. Installed versioned SDK type declarations were inspected to validate the current APIs.
- [OpenTelemetry propagator specification](https://opentelemetry.io/docs/specs/otel/context/api-propagators/) informed the trace-context-only carrier boundary. Baggage is deliberately not copied into the lab.
- [Grafana provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/) informed Git-controlled datasource/dashboard configuration and disabled dashboard UI edits.
- [Microsoft's compiler API guide](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API) informed exact AST-based documentation maps. TypeScript 6.0.3 is deliberately pinned for its stable JavaScript compiler API; TypeScript 7's main package no longer provides that API. Strict compilation and explicit Node types are still verified.

Official release/package metadata supplies exact Python/npm versions, Prometheus archive SHA-256, Grafana OCI digest and scanner/action pins in the locks. Checksums establish integrity against these reviewed pins, not independent vendor trust or indefinite safety. Advisory databases change; rescan before adapting. Dependencies, complexity, self-documenting names/contracts, explicit units, closed schemas and negative tests are used together rather than treating Big-O or comments alone as code quality.

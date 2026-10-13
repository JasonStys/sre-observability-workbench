# Measured validation and review record

Author-led validation by Jason Stys, 2026-10-13. This file will be completed with measured final CI evidence before handoff; no initial/planned check is represented as final success.

## Local measured evidence

Real Windows Python/TypeScript HTTP drill: 40 client attempts, four controlled 503 failures followed by successful requests, 120 service spans, 40 client SDK spans, 80 sanitized log records and 40 verified distributed parent chains. Reports are regenerated from the final reviewed source; aggregate measurements are in `drill.json`/`drill.html`. Exact timing is observational and includes the local machine, not production MTTR or alert-delivery delay.

Python baseline: 35 tests passed with 96.85% branch-inclusive coverage; TypeScript baseline: three real boundary/HTTP tests passed. Final counts/results will be recorded after the complete source review. Native Prometheus config and initial six scenarios passed; a seventh partial-scrape-loss regression was added when live validation exposed an incorrect down-series aggregation. Earlier local failures were development findings, not hidden/suppressed green runs.

## Author review

Security: checked local-only target/exporter boundaries, raw header/query retention, closed schemas, inert HTML, bound SQL, exclusive outputs, tool extraction/hash verification, workflow permissions and generated CI password handling. Correctness: reviewed request denominators, strict threshold equality, distinct latency/availability SLIs, counter resets, missing/future data, trace parents, Windows socket binds and cleanup. Performance: removed repeated per-event log scans/max-failure computations; use O(N) correlation indexes and O(N log N) percentile sorting. Maintainability: contracts, generated line maps, simple file layout, exhaustive README guide and operational limits.

Development fixes with regression evidence: TypeScript 7 required explicit Node type configuration; oversized response completion needed synchronous failure resolution before later end events; Windows listener reuse had to be disabled for exclusive binds; Prometheus down-series detection must **count** zero-valued filtered samples instead of summing their values. Tests were strengthened, not removed. No independent reviewer/audit, production deployment, cloud account or local Docker repair is claimed.

## Release acceptance

Require all latest-main checks green (four core lanes, actual native/vendor stack, security and both CodeQL languages), no open CodeQL alerts, clean Git status, current file/symbol maps, and no Actions artifacts/cache entries for this repo. Source snapshot/run links and final observations will be recorded after publication. Logs remain in Actions; this lab does not upload evidence artifacts because the account's included Actions storage meter is full.

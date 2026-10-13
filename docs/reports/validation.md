# Measured validation and review record

Author-led validation by Jason Stys, 2026-10-13. Reviewed executable/configuration source: `bb731ae7883e11f5c49020b3eddb105cb81f3067`. The linked completed runs and immutable `ci.json` snapshot validate that source; this documentation-only follow-up is checked again by the same workflows before handoff. Live README badges show the latest main status.

## Local measured evidence

Real Windows Python/TypeScript HTTP drill regenerated from the published reviewed source: 40 client attempts, four controlled 503 failures followed by successful requests, 120 service spans, 40 client SDK spans, 80 sanitized log records and 40 verified distributed parent chains. Aggregate measurements are in `drill.json`/`drill.html`: first failed completion 7 ms after the first completion; first completion after the final scheduled failure 53 ms after the first completion; observed batch span 192 ms. These are client timings, not production MTTR or alert-delivery delay. Availability burn is 100 and remaining observed budget is -3.96; PAGE is the correct historical-failure result, not a test failure.

Final local and CI core suites: **39 Python tests**, **four TypeScript tests**, **98.53% Windows branch-inclusive coverage** (≥90% gate), strict mypy/Ruff/TypeScript and exact documentation maps. The property test uses 150 generated outcome batches. Runtime and dev dependency audits found no known vulnerabilities; npm audit found zero. Native Prometheus 3.15.0 validated configuration, 12 rules and **seven scenarios**. Actual Windows stack validation measured two healthy targets, 40 requests/four errors, executing recording rules and a fired missing-worker alert. The 10,000-event analyzer benchmark measured median **15.585 ms** over five repetitions and **655,904 bytes** peak Python allocation; the benchmark excludes service capacity and is not an asymptotic proof.

## Verified GitHub execution

- [Validate: all six jobs passed](https://github.com/JasonStys/sre-observability-workbench/actions/runs/38474394511): Ubuntu Python 3.12/3.14, Windows Python 3.14, macOS Intel Python 3.14, security, and real observability.
- [CodeQL: both jobs passed](https://github.com/JasonStys/sre-observability-workbench/actions/runs/38474394454): Python and JavaScript/TypeScript security-extended, with zero open code-scanning alerts at verification.
- [Actual observability job](https://github.com/JasonStys/sre-observability-workbench/actions/runs/38474394511/job/115561387324): authenticated Grafana 13.2.4 provisioned seven panels and queried the actual 40-request Prometheus datasource; native scrape loss fired its alert. The CI container was removed; this PC's Docker Desktop was untouched.
- [Security job](https://github.com/JasonStys/sre-observability-workbench/actions/runs/38474394511/job/115561387712): complete dependency audits, Gitleaks history scan, Trivy HIGH/CRITICAL dependency gate, actionlint and ShellCheck passed. No advisory suppressions or test exclusions were introduced.

Both first published workflows succeeded. Earlier local prototype findings were fixed before publication, not concealed by deleting failed GitHub runs. The synthetic HTML report was opened in a browser and verified for author attribution, measured counts, explicit quality and failure states.

## Author review

Security: checked local-only target/exporter boundaries, raw header/query retention, closed schemas, inert HTML, bound SQL, exclusive outputs, tool extraction/hash verification, workflow permissions and generated CI password handling. Correctness: reviewed request denominators, strict threshold equality, distinct latency/availability SLIs, counter resets, missing/future data, trace parents, Windows socket binds and cleanup. Performance: removed repeated per-event log scans/max-failure computations; use O(N) correlation indexes and O(N log N) percentile sorting. Maintainability: contracts, generated line maps, simple file layout, exhaustive README guide and operational limits.

Development fixes with regression evidence: TypeScript required explicit Node type configuration, and compiler API documentation maps use the verified stable 6.0.3 API instead of assuming the native 7.x package still exposes it; oversized response completion needed synchronous failure resolution before later end events; Windows listener reuse had to be disabled for exclusive binds; Prometheus down-series detection must **count** zero-valued filtered samples instead of summing their values. Tests were strengthened, not removed. No independent reviewer/audit, production deployment, cloud account or local Docker repair is claimed.

## Release acceptance

Release acceptance: all latest-main checks green (four core lanes, actual native/vendor stack, security and both CodeQL languages), no open CodeQL alerts, clean Git status and current file/symbol maps. The executable source met all gates; the documentation follow-up is independently rechecked before final handoff.

This repo has **zero Actions artifacts and zero Actions cache bytes**. No cleanup, account settings changes or artifact/cache uploads were performed. Account-wide billing/storage observations are reported privately to the owner, not published as portfolio evidence. Logs/summaries remain available in Actions, with deliberately selected synthetic aggregate reports in this folder.

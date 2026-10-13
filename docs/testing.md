# Risk-based validation strategy

The highest risks are false health from missing/failing attempts, broken distributed trace propagation, private input retention, unbounded target/load behavior and a dashboard that is provisioned but cannot query data.

| Boundary | Validation |
| --- | --- |
| Evidence | Closed schema, strict integers/IDs, duplicate keys/IDs, malformed UTF-8/JSON, 8 MiB cap |
| SLO mathematics | Exact burn equality, independent latency/availability, empty/future/missing/sparse data, window endpoints, aged failures, nearest rank |
| Properties | 150 randomized outcome batches, rational budget oracle and order independence |
| Client | Strict local origin, explicit ownership acknowledgement, bounded counts, duplicate/unknown flags, real response cap, absolute deadline, no redirect following, complete IDs |
| Services | Real HTTP SDK chain, fixed endpoints, private header/baggage/query stripping, 502 on unavailable upstream, finite 503 schedule, resource cleanup, exclusive output, Windows bind behavior |
| Reports/storage | HTML escaping/CSP/no scripts/assets, exclusive output, real SQL counts and queryable indexed database |
| Prometheus | Native config/12 rules, seven rule scenarios including counter reset, partial/absent scrapes and low traffic; actual live scrape/count/rule/missing-worker alert |
| Grafana | Actual digest-pinned authenticated Linux CI runtime, seven panels, datasource health, real proxied query; not just JSON fixture validation |
| Delivery | Four OS/Python lanes, strict TypeScript, Ruff/mypy, ≥90% branch-inclusive coverage, exact AST line maps, exhaustive tracked-file guide |
| Supply chain | Full hash locks, npm integrity lock, exact action/tool/image pins, dependency audits, history secret scan, Trivy HIGH/CRITICAL dependency gate, actionlint/ShellCheck, CodeQL security-extended |

Python warnings are errors to surface leaked resources. Integration starts real owned loopback servers and executes the compiled TypeScript client; it does not replace SDK/network behavior with canned output. The CLI interruption unit test mocks only the launcher blocking path; actual teardown is separately exercised by real integration tests. Vendor dependency installation and advisory lookup require network access; tests themselves are synthetic/local.

Performance is measured, not constrained by a flaky hardware-specific millisecond gate. The benchmark checks correctness on 10,000 attempts and reports median of five wall-clock samples plus Python-allocated memory peak. SLO latency assertions use controlled synthetic values/threshold boundaries; real timing differs by runner.

Scope gaps: production workloads, long-duration endurance, massive DDoS, external alert delivery/inhibition, macOS native Prometheus binaries, public/TLS/tenancy/auth for demo Python listeners, trace UI backend and independent penetration/compliance assessment. Vendor container images are pinned and runtime-constrained; dependency scans cover authored Python/npm graphs, not a certification that every OS package inside Grafana is vulnerability-free.

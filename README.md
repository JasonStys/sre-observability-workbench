# SRE Observability Workbench

[![Validate](https://github.com/JasonStys/sre-observability-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/JasonStys/sre-observability-workbench/actions/workflows/ci.yml)
[![CodeQL](https://github.com/JasonStys/sre-observability-workbench/actions/workflows/codeql.yml/badge.svg)](https://github.com/JasonStys/sre-observability-workbench/actions/workflows/codeql.yml)

A runnable, synthetic reliability lab: drive actual HTTP requests through two services, connect Prometheus metrics to OpenTelemetry traces and structured logs, inject finite failures, and calculate evidence-aware SLOs. Created by **[Jason Stys](https://github.com/JasonStys)** · [Professional contact](https://www.linkedin.com/in/jason-stys-31b30b351/).

## What it demonstrates

- **Distributed observability:** TypeScript client → Python gateway → Python worker, real OpenTelemetry SDK spans with verified parent chains, bounded metric labels, and privacy-allowlisted logs.
- **SLO reasoning:** independent availability and successful-request latency objectives; exact rational burn calculations, multiwindow alerts, negative remaining budgets, explicit missing/low-volume states, and raw nearest-rank percentiles.
- **Incident drills:** a finite worker error schedule followed by automatic recovery; real request failures/timeouts are retained rather than removed from the denominator.
- **Operations:** native Prometheus config/rule tests and real scrape-loss alert detection; seven version-controlled Grafana panels, tested with authentication and a working datasource on a disposable Linux CI runner.
- **Evidence:** inert HTML/JSON reports and indexed, parameterized SQLite storage. Measured drill, benchmark, review and CI results live in [docs/reports](docs/reports).
- **Delivery:** strict types/lint, randomized properties, cross-platform HTTP integration, checksum-pinned tools/actions, dependency and secret scans, and Python/TypeScript CodeQL. No Actions artifact/cache uploads.

This is **not a production monitoring platform**, a compliance certification, a live government/military environment, or a load tester for arbitrary targets. Only synthetic loopback traffic is supported. No accounts, paid infrastructure, production data, third-party telemetry exporters, notification delivery or local Docker repair are involved.

## Quick start

Requirements: Python 3.12+ and Node.js 24. Commands from this repository root:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install --require-hashes -r requirements-dev.lock
npm.cmd ci --ignore-scripts
npm.cmd run build
.venv/Scripts/python scripts/drill.py --output out/my-first-drill
```

macOS/Linux: replace `.venv/Scripts/python` with `.venv/bin/python` and `npm.cmd` with `npm`. The native drill is tested on Windows, Ubuntu and macOS Intel. It starts/stops its own loopback listeners and requires no Docker. Output directories must be **new**; changing the output name preserves previous evidence.

Open `out/my-first-drill/report/assessment.html` in a browser. The default 40-attempt run injects four HTTP 503 failures among the first 12 worker calls. Later calls succeed; the historical burn alert can remain PAGE until the failures age out. Performance varies by machine; the 50 ms latency goal is intentionally illustrative, not a hard timing assertion in CI.

For interactive native metrics, in separate terminals:

```powershell
.venv/Scripts/python -m sre serve --output out/interactive --fault-every 3 --fault-until 12
node dist/load.js --target http://127.0.0.1:8000 --output out/batch --attempts 40 --ack-owned-target
```

`/health`, `/metrics` and `/work` are the only GET routes. Defaults are gateway port 8000 and worker port 8001. Ctrl+C stops both services. There is no network fault-control endpoint. [Runbook](docs/runbook.md) explains analysis, trace correlation, Prometheus, Grafana and cleanup.

## Validate locally

```powershell
npm.cmd test
.venv/Scripts/python -m pytest --cov --cov-report=term-missing
.venv/Scripts/python -m mypy
.venv/Scripts/python -m ruff check .
.venv/Scripts/python -m ruff format --check .
.venv/Scripts/python scripts/code_map.py --check
npm.cmd run maps:check
.venv/Scripts/python scripts/file_guide.py --check
.venv/Scripts/python scripts/validate_repo.py
.venv/Scripts/python scripts/benchmark.py
.venv/Scripts/python scripts/bootstrap.py promtool
.tools/promtool.exe check config ops/prometheus.yml
.tools/promtool.exe test rules ops/rules.test.yml
```

The verified Prometheus bootstrap supports Windows/Linux amd64; on Linux use `.tools/promtool`. macOS core tests do not claim native vendor binary validation. See [testing](docs/testing.md), [measured results](docs/reports/validation.md), [security](SECURITY.md), [design](docs/architecture.md), [SLO contract](docs/slo.md) and [sources](docs/research.md).

## Configuration and contribution

Offline analysis accepts target parts per million and latency microseconds. Checked-in PromQL/dashboard defaults are fixed at 99.9% and 50 ms; changing the offline objective does **not** rewrite them. Change and retest rules/dashboard explicitly when adapting the lab. Bounds, volume floor and threat-model limitations are deliberate and documented.

Every authored Python function/class has a contract; file-header symbol maps include definitions, parameters and assigned variables with exact current line numbers. TypeScript/JavaScript maps use the compiler AST; SQL/YAML/shell maps cover declared columns/configuration/variables. Generate maps **after** formatting. Stage intended files, then regenerate the exhaustive README guide. Do not commit generated raw evidence, databases, API keys, accounts or downloaded tools. See [contributing](CONTRIBUTING.md).

## Every tracked file

<!-- BEGIN FILE GUIDE -->

| File | Purpose |
| --- | --- |
| [.gitattributes](.gitattributes) | Portable LF handling for authored text. |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | Jason Stys: native cross-platform evidence, actual Prometheus/Grafana and storage-free security checks. |
| [.github/workflows/codeql.yml](.github/workflows/codeql.yml) | Jason Stys: read-only source analysis, scoped security event uploads; not Actions artifacts. |
| [.gitignore](.gitignore) | Excludes local evidence, accounts, binaries, caches and generated build output. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution and coding conventions. |
| [LICENSE](LICENSE) | MIT license for authored source, not third-party vendor code. |
| [README.md](README.md) | SRE Observability Workbench. |
| [SECURITY.md](SECURITY.md) | Security boundary and reporting. |
| [client/client.test.ts](client/client.test.ts) | Negative-boundary and real HTTP client tests. Created by Jason Stys. |
| [client/load.ts](client/load.ts) | Bounded loopback drill client, SDK spans and complete attempt evidence. Created by Jason Stys. |
| [docs/architecture.md](docs/architecture.md) | Architecture and ADR-001: a bounded native observability lab. |
| [docs/reports/benchmark.json](docs/reports/benchmark.json) | Measured in-memory analyzer timing and allocation evidence. |
| [docs/reports/ci.json](docs/reports/ci.json) | Verified source SHA and final measured GitHub Actions check snapshot. |
| [docs/reports/drill.html](docs/reports/drill.html) | Escaped network-inert rendering of the measured synthetic drill. |
| [docs/reports/drill.json](docs/reports/drill.json) | Actual synthetic Windows fault/recovery measurement and correlated evidence counts. |
| [docs/reports/stack.json](docs/reports/stack.json) | Actual Windows native Prometheus scrape/rule/missing-worker measurements. |
| [docs/reports/validation.md](docs/reports/validation.md) | Measured validation and review record. |
| [docs/research.md](docs/research.md) | Primary sources and implementation rationale. |
| [docs/runbook.md](docs/runbook.md) | Local operations and incident runbook. |
| [docs/slo.md](docs/slo.md) | Evidence, SLI and alert contracts. |
| [docs/testing.md](docs/testing.md) | Risk-based validation strategy. |
| [ops/grafana/dashboard.json](ops/grafana/dashboard.json) | Seven read-only SRE panels with attribution, missing-data caveats and fixed PromQL. |
| [ops/grafana/provisioning/dashboards/default.yml](ops/grafana/provisioning/dashboards/default.yml) | Versioned read-only dashboard provisioning. Created by Jason Stys. |
| [ops/grafana/provisioning/datasources/default.yml](ops/grafana/provisioning/datasources/default.yml) | Local native Prometheus datasource; no external SaaS or stored credentials. Created by Jason Stys. |
| [ops/prometheus.yml](ops/prometheus.yml) | Loopback-only native service scraping; no remote write or credentials. Created by Jason Stys. |
| [ops/rules.test.yml](ops/rules.test.yml) | Native PromQL fixtures: healthy, failing, slow, reset, missing, low traffic. Created by Jason Stys. |
| [ops/rules.yml](ops/rules.yml) | Gateway request SLOs: fixed 99.9% / 50ms with multiwindow burn alerts. Created by Jason Stys. |
| [ops/schema.sql](ops/schema.sql) | Local synthetic evidence with indexed time/status queries. Created by Jason Stys. |
| [package-lock.json](package-lock.json) | Complete npm package graph and integrity hashes. |
| [package.json](package.json) | Pinned Node client dependencies, build and testing commands. |
| [pyproject.toml](pyproject.toml) | Strict Python lint, type, test and coverage configuration. |
| [requirements-dev.in](requirements-dev.in) | Direct validation dependencies plus the runtime graph. |
| [requirements-dev.lock](requirements-dev.lock) | Hash-locked portable validation dependency graph. |
| [requirements.in](requirements.in) | Exact reviewed direct runtime dependencies. |
| [requirements.lock](requirements.lock) | Hash-locked portable runtime dependency graph. |
| [scripts/benchmark.py](scripts/benchmark.py) | Measure bounded SLO analysis, not service capacity or asymptotic proof. Created by Jason Stys. |
| [scripts/bootstrap.py](scripts/bootstrap.py) | Install hash-verified official native tools; extract only one fixed regular binary. Jason Stys. |
| [scripts/code\_map.py](scripts/code_map.py) | Generate/check exact Python, SQL, shell and YAML symbol positions. Created by Jason Stys. |
| [scripts/drill.py](scripts/drill.py) | Run real Python/TypeScript traffic and verify metric/log/span correlation. Created by Jason Stys. |
| [scripts/file\_guide.py](scripts/file_guide.py) | Maintain exhaustive tracked-file README summaries without reading ignored drill outputs. Jason Stys. |
| [scripts/observability.py](scripts/observability.py) | Validate real Prometheus scraping and an optional disposable CI-only Grafana dashboard. Jason Stys. |
| [scripts/ts\_map.mjs](scripts/ts_map.mjs) | Generate/check exact TypeScript and JavaScript AST symbol headers. Created by Jason Stys. |
| [scripts/validate.sh](scripts/validate.sh) | Cross-platform quality, real integration and metadata gates. Created by Jason Stys. |
| [scripts/validate\_repo.py](scripts/validate_repo.py) | Fail on unsafe telemetry/configuration metadata or undocumented dashboard drift. Created by Jason Stys. |
| [sre/\_\_init\_\_.py](sre/__init__.py) | Local synthetic SRE workbench. Created by Jason Stys; https://github.com/JasonStys. |
| [sre/\_\_main\_\_.py](sre/__main__.py) | Local-only service and evidence-assessment command line. Created by Jason Stys. |
| [sre/report.py](sre/report.py) | Publish inert escaped HTML, JSON and parameterized SQLite evidence. Created by Jason Stys. |
| [sre/service.py](sre/service.py) | Two loopback-only instrumented services with controlled startup faults. Created by Jason Stys. |
| [sre/slo.py](sre/slo.py) | Validate client evidence and calculate exact request-based SLOs. Created by Jason Stys. |
| [sre/telemetry.py](sre/telemetry.py) | Allowlisted local OpenTelemetry spans, correlated logs and bounded Prometheus labels. Jason Stys. |
| [tests/test\_cli.py](tests/test_cli.py) | CLI parsing, shutdown and sanitized failure contract tests. Created by Jason Stys. |
| [tests/test\_documentation.py](tests/test_documentation.py) | Exact source-map idempotence and function-line regression tests. Created by Jason Stys. |
| [tests/test\_services.py](tests/test_services.py) | Real service, privacy, recovery, resource and cross-language integration tests. Created by Jason Stys. |
| [tests/test\_slo.py](tests/test_slo.py) | Exact SLO algebra, boundary, schema and adversarial evidence tests. Created by Jason Stys. |
| [tools.lock.json](tools.lock.json) | Official native tool SHA-256 checksums and pinned Grafana image digest. |
| [tsconfig.json](tsconfig.json) | Strict TypeScript compiler and explicit Node type configuration. |

<!-- END FILE GUIDE -->

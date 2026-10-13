# Local operations and incident runbook

## Start, inspect and stop

Use README quickstart for the self-contained 40-request drill. Every output directory must be new. The standard drill stops all owned service threads/sockets/providers in `finally` blocks and writes events, spans, logs, metric snapshots and reports beneath that directory. A failed drill preserves partial evidence for diagnosis and does not overwrite a prior run.

For continuous inspection, `python -m sre serve --output out/interactive` binds gateway 8000/worker 8001 on literal 127.0.0.1. Optional startup-only `--fault-every 3 --fault-until 12 --delay-ms 80` causes bounded synthetic errors/latency. Ctrl+C stops both. Do not forward ports, bind publicly, use a production worker or provide actual customer traffic. A local unauthenticated listener is not a multi-user security boundary.

Run the client with its exact loopback origin and `--ack-owned-target`. Attempts range 1–1000; concurrency 1–8. Health must identify this workbench before load is sent. The client does not resolve remote target DNS or follow redirects. Every attempt has an absolute 1-second deadline and a 1 KiB response cap. It retains all outcomes including status 0. Synthetic low-volume traffic does not approximate real-user traffic coverage.

## Correlate an incident

1. Read the JSON assessment's quality state before interpreting a percentage. Verify expected counts and timestamps. A green latest request is not proof the historical SLO has recovered.
2. Find failed `status` records in `client/events.jsonl`; use `trace_id` to find the client SDK span, gateway `work` span, gateway `worker.call` span, worker span and their service logs. The verified parent chain is client → gateway → gateway outbound → worker.
3. Compare `gateway-metrics.txt` totals with completed attempts. Missing connections belong in the client failure denominator; they cannot appear in completed gateway work metrics.
4. Inspect worker error status vs gateway 502 upstream failure. Review actual stdout/tool logs locally, without uploading raw private incident evidence.
5. Restart with a new output and no faults if reproducing a baseline. Preserve prior output. Record measured detection/recovery timing scope and rerun tests after any change.

For custom offline analysis:

```powershell
.venv/Scripts/python -m sre assess out/my-first-drill/client/events.jsonl --output out/reanalysis --as-of-ms YOUR_FINAL_EVENT_TIMESTAMP --expected-events 40
```

Replace the timestamp with the last completion in your evidence; do not use a stale example value or omit unknown expected counts just to obtain a green result. `--target-ppm` / `--latency-us` customize the **offline** objective only. Database examples: `SELECT status,count(*) FROM attempts GROUP BY status;` and `SELECT id,trace_id FROM attempts WHERE at_ms > ? AND status >= ?;` with parameter binding in application code.

## Native Prometheus and Grafana

Install official checksum-pinned tools explicitly: `python scripts/bootstrap.py prometheus` and `python scripts/bootstrap.py promtool`. Native Windows/Linux amd64 only. `python scripts/observability.py --output out/stack-new` starts/stops its own native Prometheus on **loopback port 9090**, scrapes actual owned random-port services, verifies 40 requests/four errors/recording rules, stops its worker and verifies a missing-worker alert. Ensure port 9090 is free; do not reuse a stranger's listener. Logs/TSDB are local ignored output, never account data.

For manual use, run `.tools/prometheus.exe --config.file=ops/prometheus.yml --storage.tsdb.path=out/prometheus-data --web.listen-address=127.0.0.1:9090` alongside default-port interactive services. Linux uses `.tools/prometheus`. Native Prometheus is not bundled/licensed as our source. Review official vendor security updates before real deployment.

`scripts/observability.py --grafana` is intentionally **disposable Linux GitHub Actions only**. The pinned Grafana container uses a generated in-memory admin password, no anonymous access/signup, disabled analytics/update/preinstall checks, no capabilities, no-new-privileges, read-only configuration and transient state. Host networking is needed to reach native loopback Prometheus on that disposable runner; Grafana itself binds 127.0.0.1:3000. This is not an isolated production cluster. The test verifies seven panels, datasource health and the actual request count through its authenticated proxy, then removes only its uniquely named container. It never runs or repairs Docker Desktop on this PC.

Trace/log exploration is JSONL, not a Grafana trace backend. There is no notification provider, authentication for Python demo services, public hosting or retained Grafana account. If you want a long-lived dashboard, first design its account/storage/TLS/network isolation; do not copy ephemeral CI settings into production.

## Rollback and cleanup

If correlation/counts, missing-data handling, dependency gates or privacy tests fail, stop the local lab and do not publish a production adaptation. Revert only the relevant source change via a reviewed commit and rerun the whole validation suite. No cloud apply/destroy, host hardening changes, account operations or automated Actions deletion are performed.

To reclaim local space, inspect the exact lab output you created and delete it only after keeping needed evidence. The application does not purge output or unrelated files. Service evidence caps at 10,000 records/file; restart with a new directory well before long-lived demo retention fills. Logs and generated evidence are intentionally excluded from Git.

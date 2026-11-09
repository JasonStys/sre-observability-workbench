# Service and journey objective review

Created by Jason Stys. A checkout path and an inventory path can have different owners, objectives and failure patterns. Averaging them together can hide a broken low-volume journey. The `bundle` command keeps each stream independent and compares baseline/candidate policy thresholds using the **same exact evidence bytes, declared expected count, evaluation clock, trailing window and volume floor**.

Create realistic but deliberately small fictional inputs and review them offline:

```powershell
New-Item -ItemType Directory -Force out
.venv/Scripts/python scripts/journey_demo.py --output out/journey-input
.venv/Scripts/python -m sre bundle out/journey-input/bundle.json --output out/journey-review
```

Open `out/journey-review/journeys.html`. Linux/macOS equivalents use `mkdir -p out` and `.venv/bin/python`. Each output directory must be new and its parent must exist; earlier evidence is preserved.

The demo's checkout stream has 20 successful requests, two taking 80 ms. Raising its allowed latency from 50 to 100 ms changes the latency PAGE to CLEAR while preserving the same measured durations. The warehouse stream has one HTTP 503 among 20 requests; it stays PAGE under both thresholds. Both candidate latency limits are explicitly marked **loosened**. That policy change is not a measured service improvement. The owner review queue includes burns, low-volume windows, incomplete evidence and loosened targets.

The manifest contract is a closed schema-1 object with `as_of_ms` and `streams` (1–20). Each stream has `service`, `journey`, `owner`, `events`, `expected_events`, `baseline_policy` and `candidate_policy`. The two policy objects require `target_ppm`, `latency_us`, `window_ms`, `min_requests`. Window and minimum-volume floor must match between the compared policies; use separate assessments to explore those sampling changes. Expected counts are per selected window, not lifetime counts. Each events reference is one distinct JSONL filename beside the manifest; traversal, absolute paths, URLs, symlinks and junction ancestors are rejected. Duplicate service/journey pairs and repeated filenames are rejected. Input is capped at 256 KiB of manifest, 8 MiB of aggregate event bytes and 10,000 aggregate attempts. Attempt IDs need only be unique within each stream.

Results preserve both full assessments, exact source and manifest SHA-256 digests, bad-count/budget deltas and availability/latency alert transitions. Hashes identify supplied bytes; they are not authenticated provenance. Stream labels, ownership, disjointness and expected completeness remain assertions. Missing or future telemetry does not become healthy through a policy change. No cross-stream availability average or portfolio-wide health score is emitted. The offline result does not rewrite the separately tested PromQL/Grafana defaults or approve changes. CLI exit 0 means a valid comparison was produced, including PAGE/INSUFFICIENT results; exit 2 rejects input/output.

This remains a synthetic, local lab. No production traffic, external notifications, new telemetry exporters or arbitrary-target load generation are introduced. Reports have escaped text, restrictive CSP and no script/assets/network calls. Time cost is bounded by the existing per-stream sorting and SLO scans, approximately O(total events × log(max stream events)); no new background workers are needed.

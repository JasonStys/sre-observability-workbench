"""Real native SLO, objective-review and owned-service workflows with literal evidence views. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 90
# variable: PRODUCT — line 91
# variable: PROFILE — line 91
# variable: TITLE — line 92
# variable: VERSION — line 92
# variable: COLUMNS — line 93
# variable: RESOURCES — line 94
# variable: MODES — line 103
# variable: REVIEW_MODE — line 109
# variable: CHOICES — line 110
# variable: ACTIVE_FIELDS — line 111
# variable: FIELDS — line 143
# variable: SCENARIOS — line 159
# variable: HELP — line 165
# definition: scenario — line 168
# parameter: name — line 168
# variable: value — line 172
# definition: number — line 198
# parameter: high — line 198
# parameter: low — line 198
# parameter: name — line 198
# parameter: parameters — line 198
# variable: raw — line 200
# definition: policy — line 206
# parameter: parameters — line 206
# definition: analyze — line 216
# parameter: parameters — line 217
# parameter: stage — line 217
# parameter: state — line 217
# variable: mode — line 220
# variable: output — line 220
# variable: result — line 222
# variable: path — line 227
# variable: settings — line 231
# variable: extra — line 232
# variable: expected — line 233
# variable: expected — line 235
# variable: events — line 236
# variable: evidence — line 236
# variable: extra — line 236
# variable: clock — line 245
# variable: event — line 246
# variable: raw — line 249
# variable: events — line 250
# variable: clock — line 251
# variable: expected — line 252
# variable: result — line 257
# variable: files — line 259
# variable: path — line 261
# variable: event — line 272
# variable: candidate — line 275
# variable: manifest — line 281
# variable: compared — line 302
# variable: path — line 307
# variable: summary — line 311
# variable: summary — line 313
# definition: views — line 317
# parameter: files — line 317
# variable: result — line 319
# variable: report — line 321
# variable: key — line 324
# variable: line — line 327
# variable: journeys — line 330
# variable: evidence — line 334
# variable: service — line 338
# variable: line — line 339
# definition: cells — line 345
# parameter: row — line 345
# END CODE MAP

from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from . import bundle
from .desktop_drill import drill
from .desktop_io import Rejected, canonical, json_value, read_bytes
from .desktop_state import Workspace
from .report import publish
from .service import Faults
from .slo import MAX_BYTES, MAX_EVENTS, Policy, assess, integer, parse_events

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
PRODUCT, PROFILE = "sre-observability-workbench", "SreObservabilityWorkbench"
TITLE, VERSION = "SRE Observability Workbench", "1.1.1"
COLUMNS = ("Service / journey", "Signal / attempt", "Evidence", "State / result")
RESOURCES = (
    "ops/schema.sql",
    "examples/desktop/bundle.json",
    "examples/desktop/checkout.jsonl",
    "examples/desktop/warehouse.jsonl",
    "notices.txt",
    "app.ico",
    "python314.dll",
)
MODES = (
    "Run owned fault/recovery drill",
    "Assess request evidence",
    "Compare objective settings",
    "Review service/journey bundle",
)
REVIEW_MODE: str | None = None
CHOICES: dict[str, tuple[str, ...]] = {}
ACTIVE_FIELDS = {
    MODES[0]: (
        "attempts",
        "fault_every",
        "fault_until",
        "delay_ms",
        "target_ppm",
        "latency_us",
        "min_requests",
    ),
    MODES[1]: (
        "events",
        "as_of_ms",
        "expected_events",
        "target_ppm",
        "latency_us",
        "window_ms",
        "min_requests",
    ),
    MODES[2]: (
        "events",
        "as_of_ms",
        "expected_events",
        "target_ppm",
        "latency_us",
        "window_ms",
        "min_requests",
        "candidate_target",
        "candidate_latency",
    ),
    MODES[3]: ("manifest",),
}
FIELDS = (
    ("events", "Authorized synthetic request evidence (JSONL)", "file"),
    ("as_of_ms", "Evaluation finish UTC milliseconds", "text"),
    ("expected_events", "Expected attempts (blank = completeness unverified)", "text"),
    ("target_ppm", "Baseline success target (parts per million)", "text"),
    ("latency_us", "Baseline successful-request latency (microseconds)", "text"),
    ("window_ms", "Evaluation window (milliseconds)", "text"),
    ("min_requests", "Minimum window request volume", "text"),
    ("candidate_target", "Candidate success target (parts per million)", "text"),
    ("candidate_latency", "Candidate latency (microseconds)", "text"),
    ("manifest", "Service/journey bundle JSON (local JSONL siblings)", "file"),
    ("attempts", "Owned loopback attempts (1–50; no arbitrary target)", "text"),
    ("fault_every", "Return failure every Nth early worker call (0 = off)", "text"),
    ("fault_until", "Last worker call eligible for injected failure", "text"),
    ("delay_ms", "Synthetic worker delay (0–100 milliseconds)", "text"),
)
SCENARIOS = (
    "Fictional local fault and recovery",
    "Fictional slow checkout evidence",
    "Fictional retail journey ownership",
    "Same-evidence objective change",
)
HELP = "Run a finite synthetic drill against two newly owned numeric-loopback services, or select supported synthetic JSONL/bundle inputs. No arbitrary target, cloud exporter, credential, production monitoring or configuration change is offered. Availability and latency denominators include actual failures. Missing expected counts and low volume remain uncertain. Loosened objectives are a review item, never an operational improvement. The portable Python client verifies real gateway/worker spans; the original TypeScript SDK client and native Prometheus/Grafana checks remain separate CLI/CI workflows. Parameters use explicit integer units. Local history and exports are plaintext OS-owner evidence, not authentication or an availability SLA."


def scenario(name: str) -> dict[str, str]:
    """Populate the real controls with optional authored inputs, without executing or auto-approving them."""
    if name not in SCENARIOS:
        raise Rejected("unknown prepared scenario")
    value = {
        "mode": MODES[0],
        "events": str(ROOT / "examples/desktop/checkout.jsonl"),
        "as_of_ms": "1794225600000",
        "expected_events": "20",
        "target_ppm": "999000",
        "latency_us": "50000",
        "window_ms": "2592000000",
        "min_requests": "20",
        "candidate_target": "999000",
        "candidate_latency": "100000",
        "manifest": str(ROOT / "examples/desktop/bundle.json"),
        "attempts": "40",
        "fault_every": "3",
        "fault_until": "12",
        "delay_ms": "0",
    }
    if name == SCENARIOS[1]:
        value["mode"] = MODES[1]
    elif name == SCENARIOS[2]:
        value["mode"] = MODES[3]
    elif name == SCENARIOS[3]:
        value["mode"] = MODES[2]
    return value


def number(parameters: dict[str, str], name: str, low: int, high: int) -> int:
    """Require explicit bounded base-ten integers, rather than coercing floating units or blank values."""
    raw = parameters[name].strip()
    if not raw.isascii() or not raw.isdecimal() or len(raw) > 16:
        raise Rejected("setting requires a bounded base-ten integer")
    return integer(int(raw), low, high)


def policy(parameters: dict[str, str]) -> Policy:
    """Use the same original exact-unit policy constructor and its existing finite limits."""
    return Policy(
        target_ppm=number(parameters, "target_ppm", 1, 999999),
        latency_us=number(parameters, "latency_us", 1, 10000000),
        window_ms=number(parameters, "window_ms", 1, 2678400000),
        min_requests=number(parameters, "min_requests", 1, MAX_EVENTS),
    )


def analyze(
    state: Workspace, parameters: dict[str, str], stage: Path
) -> tuple[str, str, dict[str, bytes]]:
    """Run actual core assessment, independent journey review or finite owned traffic; preserve complete raw attempt evidence."""
    mode, output = parameters["mode"], stage / "bundle"
    if mode == MODES[3]:
        result = bundle.analyze(Path(parameters["manifest"]))
        bundle.publish(result, output)
        return (
            mode,
            f"{result['stream_count']} independent journeys; {len(result['review_queue'])} owner review items",
            {path.name: read_bytes(path, MAX_BYTES) for path in output.iterdir()},
        )
    if mode not in MODES[:3]:
        raise Rejected("unsupported native operation")
    settings = policy(parameters)
    extra: dict[str, bytes] = {}
    expected: int | None
    if mode == MODES[0]:
        expected = number(parameters, "attempts", 1, 50)
        events, evidence, extra = drill(
            stage,
            expected,
            Faults(
                number(parameters, "fault_every", 0, 100),
                number(parameters, "fault_until", 0, 1000),
                number(parameters, "delay_ms", 0, 100),
            ),
        )
        clock = max(
            (event.at_ms for event in events), default=time.time_ns() // 1_000_000
        )
    else:
        raw = read_bytes(Path(parameters["events"]), MAX_BYTES)
        events = parse_events(raw)
        clock = number(parameters, "as_of_ms", 0, 4102444800000)
        expected = (
            number(parameters, "expected_events", 0, MAX_EVENTS)
            if parameters["expected_events"].strip()
            else None
        )
    result = assess(events, settings, clock, expected)
    publish(result, events, output)
    files = {
        path.name: read_bytes(path, 32 * 1024 * 1024)
        for path in output.iterdir()
        if mode != MODES[0] or path.name != "evidence.db"
    }
    files["events.jsonl"] = b"".join(
        json.dumps(
            {"schema": 1, **asdict(event)},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
        + b"\n"
        for event in events
    )
    if mode == MODES[2]:
        candidate = Policy(
            target_ppm=number(parameters, "candidate_target", 1, 999999),
            latency_us=number(parameters, "candidate_latency", 1, 10000000),
            window_ms=settings.window_ms,
            min_requests=settings.min_requests,
        )
        manifest = {
            "schema": 1,
            "as_of_ms": clock,
            "streams": [
                {
                    "service": "selected-evidence",
                    "journey": "same-evidence-review",
                    "owner": "Operator must establish actual ownership",
                    "events": "events.jsonl",
                    "expected_events": len(events) if expected is None else expected,
                    "baseline_policy": asdict(settings),
                    "candidate_policy": asdict(candidate),
                }
            ],
        }
        if expected is None:
            raise Rejected(
                "objective comparison needs an explicitly asserted expected count"
            )
        (stage / "events.jsonl").write_bytes(files["events.jsonl"])
        (stage / "manifest.json").write_bytes(canonical(manifest))
        compared = bundle.analyze(stage / "manifest.json")
        bundle.publish(compared, stage / "comparison")
        files.update(
            {
                path.name: read_bytes(path, MAX_BYTES)
                for path in (stage / "comparison").iterdir()
            }
        )
    files.update(extra)
    summary = f"{len(events)} attempts; availability {result['availability']['alert']} ({result['availability']['bad']} bad); latency {result['latency']['alert']}; {result['quality']}"
    if mode == MODES[0]:
        summary += f"; {evidence['correlated_attempts']} service chains / {len(evidence['evidence_gaps'])} evidence gaps"
    return mode, summary, files


def views(files: dict[str, bytes]) -> dict[str, list[dict[str, Any]]]:
    """Expose actual objective states, exact request records and owner/gap queues without pooling unrelated journeys."""
    result: dict[str, list[dict[str, Any]]] = {}
    if "assessment.json" in files:
        report = json_value(files["assessment.json"])
        result["Availability and latency"] = [
            {"signal": key, "quality": report["quality"], **report[key]}
            for key in ("availability", "latency")
        ]
        result["Actual request attempts"] = [
            json_value(line) for line in files["events.jsonl"].splitlines()
        ]
    if "journeys.json" in files:
        journeys = json_value(files["journeys.json"])
        result["Independent journey objectives"] = journeys["streams"]
        result["Owner review queue"] = journeys["review_queue"]
    if "drill.json" in files:
        evidence = json_value(files["drill.json"])
        result["Service evidence gaps"] = evidence["evidence_gaps"]
        result["Real service spans"] = [
            json.loads(line)
            for service in ("gateway", "worker")
            for line in files[f"{service}-spans.jsonl"].splitlines()
        ]
        result["Drill scope and completion"] = [evidence]
    return result


def cells(row: dict[str, Any]) -> tuple[str, str, str, str]:
    """Render literal, bounded identifying values; the full selected record remains inspectable."""
    return (
        str(row.get("service", "selected-evidence"))
        + (" / " + str(row["journey"]) if "journey" in row else ""),
        str(row.get("signal", row.get("id", row.get("name", "review")))),
        str(
            row.get(
                "quality",
                row.get(
                    "reason",
                    ", ".join(row.get("reasons", []))
                    or row.get("trace_id", "inspect detail"),
                ),
            )
        ),
        str(
            row.get(
                "alert",
                row.get(
                    "status",
                    "REVIEW"
                    if row.get("reasons") or row.get("loosened_thresholds")
                    else "inspect detail",
                ),
            )
        ),
    )

"""Run real Python/TypeScript traffic and verify metric/log/span correlation. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 75
# variable: DEFAULT_FAULTS — line 82
# definition: fetch — line 85
# parameter: port — line 85
# parameter: route — line 85
# variable: connection — line 87
# variable: response — line 90
# variable: content — line 91
# definition: drill — line 99
# parameter: attempts — line 100
# parameter: faults — line 100
# parameter: output — line 100
# variable: node — line 105
# variable: lab — line 109
# variable: completed — line 110
# variable: client_result — line 129
# variable: server — line 130
# variable: events — line 134
# variable: spans — line 135
# variable: service — line 137
# variable: line — line 138
# variable: logs — line 142
# variable: service — line 144
# variable: line — line 145
# variable: client_spans — line 149
# variable: line — line 151
# variable: by_trace — line 162
# variable: span — line 163
# variable: logs_by_trace — line 165
# variable: log — line 166
# variable: client_by_trace — line 168
# variable: span — line 168
# variable: event — line 169
# variable: trace_spans — line 170
# variable: gateway — line 171
# variable: span — line 173
# variable: outbound — line 176
# variable: span — line 176
# variable: span — line 177
# variable: worker — line 177
# variable: matching_logs — line 186
# variable: log — line 188
# variable: as_of_ms — line 191
# variable: event — line 191
# variable: report — line 192
# variable: event — line 193
# variable: failed — line 193
# variable: item — line 194
# variable: last_failed_id — line 194
# variable: event — line 195
# variable: healthy_after — line 195
# variable: service — line 214
# variable: metrics — line 215
# variable: count — line 216
# variable: group — line 216
# definition: main — line 225
# variable: parser — line 227
# variable: arguments — line 230
# variable: result — line 231
# END CODE MAP

from __future__ import annotations

import argparse
import http.client
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sre.report import publish  # noqa: E402
from sre.service import Faults, Lab  # noqa: E402
from sre.slo import Policy, assess, load_events  # noqa: E402

DEFAULT_FAULTS = Faults(3, 12, 0)


def fetch(port: int, route: str) -> str:
    """Read bounded output from a server owned by the current lab, using a fixed local route."""
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        connection.request("GET", route)
        response = connection.getresponse()
        content = response.read(256 * 1024)
        if response.status != 200:
            raise ValueError("owned lab response was unsuccessful")
        return content.decode()
    finally:
        connection.close()


def drill(
    output: Path, attempts: int = 40, faults: Faults = DEFAULT_FAULTS
) -> dict[str, Any]:
    """Drive a finite error/recovery schedule and prove each client attempt has matching service evidence."""
    if not (ROOT / "dist/load.js").is_file():
        raise ValueError("compile the TypeScript client with npm run build first")
    node = shutil.which("node")
    if node is None:
        raise ValueError("Node.js 24 is required")
    output.mkdir(parents=True, mode=0o700, exist_ok=False)
    with Lab(output / "services", faults) as lab:
        completed = subprocess.run(
            [
                node,
                str(ROOT / "dist/load.js"),
                "--target",
                f"http://127.0.0.1:{lab.gateway_port}",
                "--output",
                str(output / "client"),
                "--attempts",
                str(attempts),
                "--concurrency",
                "1",
                "--ack-owned-target",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        client_result = json.loads(completed.stdout)
        for server in lab.servers:
            (output / f"{server.telemetry.service}-metrics.txt").write_text(
                fetch(server.server_port, "/metrics"), encoding="utf-8"
            )
    events = load_events(output / "client/events.jsonl")
    spans = [
        json.loads(line)
        for service in ("gateway", "worker")
        for line in (output / f"services/{service}-spans.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    logs = [
        json.loads(line)
        for service in ("gateway", "worker")
        for line in (output / f"services/{service}-logs.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    client_spans = [
        json.loads(line)
        for line in (output / "client/client-spans.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    if (
        len(events) != attempts
        or len(spans) != attempts * 3
        or len(logs) != attempts * 2
        or len(client_spans) != attempts
    ):
        raise ValueError("incomplete cross-service evidence")
    by_trace: dict[str, list[dict[str, Any]]] = {}
    for span in spans:
        by_trace.setdefault(span["trace_id"], []).append(span)
    logs_by_trace: dict[str, list[dict[str, Any]]] = {}
    for log in logs:
        logs_by_trace.setdefault(log["trace_id"], []).append(log)
    client_by_trace = {span["trace_id"]: span for span in client_spans}
    for event in events:
        trace_spans = by_trace[event.trace_id]
        gateway = next(
            span
            for span in trace_spans
            if span["service"] == "gateway" and span["name"] == "work"
        )
        outbound = next(span for span in trace_spans if span["name"] == "worker.call")
        worker = next(span for span in trace_spans if span["service"] == "worker")
        if (gateway["parent_id"], outbound["parent_id"], worker["parent_id"]) != (
            event.span_id,
            gateway["span_id"],
            outbound["span_id"],
        ):
            raise ValueError("broken distributed trace parent chain")
        if client_by_trace[event.trace_id]["span_id"] != event.span_id:
            raise ValueError("client SDK evidence disagrees with attempt correlation")
        matching_logs = logs_by_trace[event.trace_id]
        if len(matching_logs) != 2 or any(
            log["status"] != event.status for log in matching_logs
        ):
            raise ValueError("logs disagree with observed request outcomes")
    as_of_ms = max(event.at_ms for event in events)
    report = assess(events, Policy(), as_of_ms, attempts)
    failed = [event for event in events if event.status != 200]
    last_failed_id = max((item.id for item in failed), default=0)
    healthy_after = [event for event in events if failed and event.id > last_failed_id]
    report["drill"] = {
        "attempts": attempts,
        "failures": len(failed),
        "service_spans": len(spans),
        "client_spans": len(client_spans),
        "correlated_logs": len(logs),
        "parent_chains_verified": attempts,
        "first_failure_ms_from_first_completion": failed[0].at_ms - events[0].at_ms
        if failed
        else None,
        "first_recovered_completion_ms_from_first_completion": healthy_after[0].at_ms
        - events[0].at_ms
        if healthy_after
        else None,
        "timing_scope": "client completions, not alert notification or production MTTR",
        "client_result": client_result,
    }
    publish(report, events, output / "report")
    for service in ("gateway", "worker"):
        metrics = (output / f"{service}-metrics.txt").read_text(encoding="utf-8")
        for group, count in (("2xx", attempts - len(failed)), ("5xx", len(failed))):
            if (
                f'workbench_requests_total{{service="{service}",status_group="{group}"}} {count}.0'
                not in metrics
            ):
                raise ValueError("scraped metrics disagree with client attempts")
    return report


def main() -> int:
    """Run only an explicitly requested new local drill; keep transient evidence outside Git by default."""
    parser = argparse.ArgumentParser(description="Synthetic local drill by Jason Stys")
    parser.add_argument("--output", type=Path, default=ROOT / "out/drill")
    parser.add_argument("--attempts", type=int, default=40)
    arguments = parser.parse_args()
    result = drill(arguments.output, arguments.attempts)
    print(json.dumps(result["drill"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

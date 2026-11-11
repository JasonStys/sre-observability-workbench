"""Finite native-client traffic through the existing owned instrumented services, never arbitrary targets. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: drill — line 65
# parameter: attempts — line 66
# parameter: faults — line 66
# parameter: stage — line 66
# variable: events — line 70
# variable: deadline — line 71
# variable: lab — line 72
# variable: number — line 73
# variable: trace — line 76
# variable: span — line 77
# variable: connection — line 78
# variable: started — line 81
# variable: status — line 82
# variable: response — line 87
# variable: body — line 88
# variable: status — line 90
# variable: raw — line 110
# variable: service — line 114
# variable: kind — line 115
# variable: spans — line 117
# variable: service — line 119
# variable: line — line 120
# variable: logs — line 122
# variable: service — line 124
# variable: line — line 125
# variable: by_trace — line 127
# variable: span_row — line 128
# variable: by_log — line 130
# variable: log — line 131
# variable: correlated — line 133
# variable: gaps — line 133
# variable: event — line 134
# variable: messages — line 135
# variable: rows — line 135
# variable: gateway — line 139
# variable: row — line 140
# variable: outbound — line 142
# variable: row — line 144
# variable: worker — line 147
# variable: row — line 148
# variable: valid — line 150
# variable: valid — line 156
# variable: message — line 160
# variable: correlated — line 163
# variable: evidence — line 173
# variable: event — line 177
# END CODE MAP

from __future__ import annotations

import http.client
import json
import secrets
import time
from pathlib import Path
from typing import Any

from .desktop_io import canonical, read_bytes
from .service import Faults, Lab
from .slo import Event, integer


def drill(
    stage: Path, attempts: int, faults: Faults
) -> tuple[list[Event], dict[str, Any], dict[str, bytes]]:
    """Retain every actual attempt; a fixed 15-second schedule deadline stops new requests and exposes missing work."""
    integer(attempts, 1, 50)
    events = []
    deadline = time.monotonic() + 15
    with Lab(stage / "services", faults) as lab:
        for number in range(1, attempts + 1):
            if time.monotonic() >= deadline:
                break
            trace = format(secrets.randbits(128) or 1, "032x")
            span = format(secrets.randbits(64) or 1, "016x")
            connection = http.client.HTTPConnection(
                "127.0.0.1", lab.gateway_port, timeout=1
            )
            started = time.perf_counter()
            status = 0
            try:
                connection.request(
                    "GET", "/work", headers={"traceparent": f"00-{trace}-{span}-01"}
                )
                response = connection.getresponse()
                body = response.read(1025)
                if len(body) <= 1024 and response.status in (200, 503, 502, 504):
                    status = response.status
            except (OSError, http.client.HTTPException):
                pass  # Status 0 is a retained client failure, never a successful fallback.
            finally:
                connection.close()
            events.append(
                Event.parse(
                    {
                        "schema": 1,
                        "id": number,
                        "at_ms": time.time_ns() // 1_000_000,
                        "duration_us": round(
                            (time.perf_counter() - started) * 1_000_000
                        ),
                        "status": status,
                        "trace_id": trace,
                        "span_id": span,
                    }
                )
            )
    raw = {
        f"{service}-{kind}.jsonl": read_bytes(
            stage / f"services/{service}-{kind}.jsonl", 8 * 1024 * 1024
        )
        for service in ("gateway", "worker")
        for kind in ("spans", "logs")
    }
    spans = [
        json.loads(line)
        for service in ("gateway", "worker")
        for line in raw[f"{service}-spans.jsonl"].splitlines()
    ]
    logs = [
        json.loads(line)
        for service in ("gateway", "worker")
        for line in raw[f"{service}-logs.jsonl"].splitlines()
    ]
    by_trace: dict[str, list[dict[str, Any]]] = {}
    for span_row in spans:
        by_trace.setdefault(span_row["trace_id"], []).append(span_row)
    by_log: dict[str, list[dict[str, Any]]] = {}
    for log in logs:
        by_log.setdefault(log["trace_id"], []).append(log)
    correlated, gaps = 0, []
    for event in events:
        rows, messages = (
            by_trace.get(event.trace_id, []),
            by_log.get(event.trace_id, []),
        )
        gateway = [
            row for row in rows if row["service"] == "gateway" and row["name"] == "work"
        ]
        outbound = [
            row
            for row in rows
            if row["service"] == "gateway" and row["name"] == "worker.call"
        ]
        worker = [
            row for row in rows if row["service"] == "worker" and row["name"] == "work"
        ]
        valid = (
            len(rows) == 3
            and len(gateway) == len(outbound) == len(worker) == 1
            and len(messages) == 2
        )
        if valid:
            valid = (
                gateway[0]["parent_id"] == event.span_id
                and outbound[0]["parent_id"] == gateway[0]["span_id"]
                and worker[0]["parent_id"] == outbound[0]["span_id"]
                and all(message["status"] == event.status for message in messages)
            )
        if valid:
            correlated += 1
        else:
            gaps.append(
                {
                    "id": event.id,
                    "trace_id": event.trace_id,
                    "status": event.status,
                    "reason": "service evidence incomplete or inconsistent with actual client observation",
                }
            )
    evidence = {
        "kind": "owned_native_loopback_drill",
        "requested_attempts": attempts,
        "completed_attempts": len(events),
        "failures": sum(not 200 <= event.status < 300 for event in events),
        "service_spans": len(spans),
        "service_logs": len(logs),
        "correlated_attempts": correlated,
        "evidence_gaps": gaps,
        "deadline_exhausted": len(events) < attempts,
        "scope": "Python native client declares W3C context; three real gateway/worker SDK spans are checked. This does not export a client SDK span or run the separate TypeScript/Prometheus/Grafana validation path.",
    }
    raw["drill.json"] = canonical(evidence)
    return events, evidence, raw

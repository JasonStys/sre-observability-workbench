"""Real service, privacy, recovery, resource and cross-language integration tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: call — line 60
# parameter: headers — line 61
# parameter: method — line 61
# parameter: port — line 61
# parameter: route — line 61
# variable: connection — line 64
# variable: response — line 67
# definition: test_native_drill — line 73
# parameter: tmp_path — line 73
# variable: result — line 75
# variable: connection — line 79
# definition: test_endpoints_privacy_and_failure — line 92
# parameter: tmp_path — line 92
# variable: marker — line 94
# variable: lab — line 95
# variable: headers — line 106
# variable: path — line 119
# variable: spans — line 121
# variable: line — line 123
# variable: span — line 125
# definition: test_boundaries_and_cleanup — line 128
# parameter: tmp_path — line 128
# variable: kwargs — line 130
# variable: lab — line 137
# variable: exporter — line 145
# definition: test_inert_report_and_exclusive_output — line 150
# parameter: tmp_path — line 150
# variable: destination — line 152
# variable: page — line 154
# definition: test_latency_drill_and_volume — line 163
# parameter: tmp_path — line 163
# variable: result — line 165
# definition: test_capacity_and_retention — line 171
# parameter: tmp_path — line 171
# variable: lab — line 175
# variable: server — line 176
# variable: _ — line 177
# variable: _ — line 183
# variable: exporter — line 187
# variable: fake — line 188
# END CODE MAP

from __future__ import annotations

import http.client
import json
import sqlite3
from pathlib import Path

import pytest

from scripts.drill import drill
from sre.report import publish
from sre.service import Faults, Lab
from sre.telemetry import LocalExporter, Telemetry, parent_context


def call(
    port: int, route: str, method: str = "GET", headers: dict[str, str] | None = None
) -> tuple[int, bytes]:
    """Send one bounded request to the explicitly owned local server and always close the socket."""
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        connection.request(method, route, headers=headers or {})
        response = connection.getresponse()
        return response.status, response.read(256 * 1024)
    finally:
        connection.close()


def test_native_drill(tmp_path: Path) -> None:
    """Real SDK/client/service/metrics/logs/traces/SQL pipeline must capture finite faults and automatic recovery."""
    result = drill(tmp_path / "drill")
    assert result["drill"]["failures"] == 4
    assert result["drill"]["parent_chains_verified"] == 40
    assert result["availability"]["alert"] == "PAGE"
    connection = sqlite3.connect(tmp_path / "drill/report/evidence.db")
    try:
        assert (
            connection.execute(
                "SELECT count(*) FROM attempts WHERE status = 503"
            ).fetchone()[0]
            == 4
        )
        assert connection.execute("SELECT count(*) FROM attempts").fetchone()[0] == 40
    finally:
        connection.close()


def test_endpoints_privacy_and_failure(tmp_path: Path) -> None:
    """Discard baggage/query/headers; reject unsupported methods and malformed bodies without echoing secrets."""
    marker = "FICTIONAL_PRIVATE_INPUT_DO_NOT_RETAIN"
    with Lab(tmp_path / "services", Faults(2, 4, 1)) as lab:
        assert call(lab.gateway_port, "/health")[0] == 200
        assert call(lab.gateway_port, "/work?private=" + marker)[0] == 404
        assert call(lab.gateway_port, "/work", "POST")[0] == 501
        assert (
            call(lab.gateway_port, "/work", headers={"Content-Length": "1"})[0] == 400
        )
        assert (
            call(lab.gateway_port, "/work", headers={"Transfer-Encoding": "chunked"})[0]
            == 400
        )
        headers = {
            "traceparent": "00-" + "1" * 32 + "-" + "2" * 16 + "-01",
            "baggage": marker,
            "Authorization": marker,
        }
        assert call(lab.gateway_port, "/work", headers=headers)[0] == 200
        assert (
            call(lab.gateway_port, "/work", headers={"traceparent": marker})[0] == 503
        )
        assert call(lab.gateway_port, "/metrics")[0] == 200
        # A unavailable upstream must produce a failure, not a successful synthetic fallback.
        lab.servers[1].upstream = 1
        assert call(lab.gateway_port, "/work")[0] == 502
    for path in (tmp_path / "services").glob("*.jsonl"):
        assert marker not in path.read_text(encoding="utf-8")
    spans = [
        json.loads(line)
        for line in (tmp_path / "services/gateway-spans.jsonl").read_text().splitlines()
    ]
    assert any(span["trace_id"] == "1" * 32 for span in spans)


def test_boundaries_and_cleanup(tmp_path: Path) -> None:
    """Reject unbounded faults, unknown services and preexisting output; clean a partial bind failure."""
    for kwargs in [{"every": 101}, {"until": 1001}, {"delay_ms": 101}]:
        with pytest.raises(ValueError):
            Faults(**kwargs)
    with pytest.raises(ValueError):
        Telemetry("other", tmp_path)
    with pytest.raises(FileExistsError):
        Lab(tmp_path)
    with Lab(tmp_path / "running") as lab:
        with pytest.raises(OSError):
            Lab(tmp_path / "partial", worker_port=lab.gateway_port)
        assert call(lab.gateway_port, "/work")[0] == 200
    assert not parent_context(None)
    assert not parent_context("00-" + "0" * 32 + "-" + "2" * 16 + "-01")
    assert not parent_context("00-" + "1" * 32 + "-" + "0" * 16 + "-01")
    assert not parent_context("00-" + "1" * 32 + "-" + "2" * 16 + "-ff")
    exporter = LocalExporter(tmp_path / "empty-spans.jsonl")
    assert exporter.export([]).name == "SUCCESS"
    exporter.shutdown()


def test_inert_report_and_exclusive_output(tmp_path: Path) -> None:
    """Injected HTML is escaped, the report is network-inert, and existing output is never overwritten."""
    destination = tmp_path / "report"
    publish({"note": "<script>alert('fictional')</script>"}, [], destination)
    page = (destination / "assessment.html").read_text(encoding="utf-8")
    assert "<script>" not in page
    assert "&lt;script&gt;" in page
    assert "default-src 'none'" in page
    assert "https://" not in page
    with pytest.raises(FileExistsError):
        publish({}, [], destination)


def test_latency_drill_and_volume(tmp_path: Path) -> None:
    """Real delayed successful worker calls exceed the illustrative threshold without availability failures."""
    result = drill(tmp_path / "slow", attempts=20, faults=Faults(delay_ms=80))
    assert result["availability"]["bad"] == 0
    assert result["latency"]["bad"] == 20
    assert result["latency"]["alert"] == "PAGE"


def test_capacity_and_retention(tmp_path: Path) -> None:
    """A saturated service rejects connections without spawning threads; capped evidence streams stay bounded."""
    from unittest.mock import MagicMock

    with Lab(tmp_path / "capped") as lab:
        server = lab.servers[1]
        for _ in range(16):
            assert server.slots.acquire(blocking=False)
        try:
            with pytest.raises((OSError, http.client.HTTPException)):
                call(lab.gateway_port, "/work")
        finally:
            for _ in range(16):
                server.slots.release()
        server.telemetry.log_count = 10_000
        assert call(lab.gateway_port, "/work")[0] == 200
    exporter = LocalExporter(tmp_path / "capped-spans.jsonl")
    fake = MagicMock()
    fake.get_span_context.return_value = None
    try:
        assert exporter.export([fake]).name == "FAILURE"
        exporter.count = 10_000
        assert exporter.export([fake]).name == "FAILURE"
    finally:
        exporter.shutdown()

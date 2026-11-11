"""Real service, privacy, recovery, resource and cross-language integration tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: call — line 80
# parameter: headers — line 81
# parameter: method — line 81
# parameter: port — line 81
# parameter: route — line 81
# variable: connection — line 84
# variable: response — line 87
# definition: test_actual_threaded_loopback_start_never_uses_reverse_dns — line 93
# parameter: monkeypatch — line 93
# parameter: tmp_path — line 93
# definition: forbidden — line 96
# parameter: _args — line 96
# parameter: _kwargs — line 96
# definition: actual_services — line 102
# variable: lab — line 104
# variable: identities — line 105
# variable: server — line 106
# variable: pool — line 112
# variable: identities — line 113
# variable: _ — line 114
# variable: name — line 114
# variable: _ — line 115
# variable: port — line 115
# variable: _ — line 116
# variable: port — line 116
# definition: test_native_drill — line 119
# parameter: tmp_path — line 119
# variable: result — line 121
# variable: connection — line 125
# definition: test_endpoints_privacy_and_failure — line 138
# parameter: tmp_path — line 138
# variable: marker — line 140
# variable: lab — line 141
# variable: headers — line 152
# variable: path — line 165
# variable: spans — line 167
# variable: line — line 169
# variable: span — line 171
# definition: test_boundaries_and_cleanup — line 174
# parameter: tmp_path — line 174
# variable: kwargs — line 176
# variable: lab — line 183
# variable: exporter — line 191
# definition: test_inert_report_and_exclusive_output — line 196
# parameter: tmp_path — line 196
# variable: destination — line 198
# variable: page — line 200
# definition: test_latency_drill_and_volume — line 209
# parameter: tmp_path — line 209
# variable: result — line 211
# definition: test_capacity_and_retention — line 217
# parameter: tmp_path — line 217
# variable: lab — line 221
# variable: server — line 222
# variable: _ — line 223
# variable: _ — line 229
# variable: exporter — line 233
# variable: fake — line 234
# END CODE MAP

from __future__ import annotations

import http.client
import json
import socket
import sqlite3
from concurrent.futures import ThreadPoolExecutor
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


def test_actual_threaded_loopback_start_never_uses_reverse_dns(tmp_path, monkeypatch):
    """Real numeric-loopback services must start/respond/close from a worker even with DNS forbidden."""

    def forbidden(*_args, **_kwargs):
        """Any reverse-lookup attempt is a failed contract, not a successful resolver fallback."""
        raise AssertionError("A numeric owned listener must not request reverse DNS")

    monkeypatch.setattr(socket, "getfqdn", forbidden)

    def actual_services():
        """Run the same real servers and request path as the native worker, using only owned ephemeral ports."""
        with Lab(tmp_path / "threaded-services") as lab:
            identities = [
                (server.server_name, server.server_port) for server in lab.servers
            ]
            assert call(lab.gateway_port, "/health")[0] == 200
            assert call(lab.gateway_port, "/work")[0] == 200
            return identities

    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="owned-no-dns") as pool:
        identities = pool.submit(actual_services).result(timeout=5)
    assert [name for name, _ in identities] == ["127.0.0.1", "127.0.0.1"]
    assert len({port for _, port in identities}) == 2
    assert all(0 < port <= 65535 for _, port in identities)


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

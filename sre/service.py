"""Two loopback-only instrumented services with controlled startup faults. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: Faults — line 114
# variable: every — line 117
# variable: until — line 118
# variable: delay_ms — line 119
# definition: __post_init__ — line 121
# parameter: self — line 121
# definition: Server — line 128
# variable: daemon_threads — line 131
# variable: block_on_close — line 132
# variable: request_queue_size — line 133
# variable: allow_reuse_address — line 135
# definition: __init__ — line 137
# parameter: faults — line 138
# parameter: port — line 138
# parameter: self — line 138
# parameter: telemetry — line 138
# parameter: upstream — line 138
# definition: process_request — line 152
# parameter: client_address — line 153
# parameter: request — line 153
# parameter: self — line 153
# definition: process_request_thread — line 165
# parameter: client_address — line 166
# parameter: request — line 166
# parameter: self — line 166
# definition: next_status — line 174
# parameter: self — line 174
# variable: fail — line 178
# definition: Handler — line 187
# variable: server — line 190
# definition: setup — line 192
# parameter: self — line 192
# definition: log_message — line 197
# parameter: args — line 197
# parameter: format — line 197
# parameter: self — line 197
# definition: send_error — line 200
# parameter: code — line 201
# parameter: explain — line 201
# parameter: message — line 201
# parameter: self — line 201
# definition: reply — line 206
# parameter: body — line 207
# parameter: content_type — line 207
# parameter: self — line 207
# parameter: status — line 207
# definition: do_GET — line 224
# parameter: self — line 224
# definition: work — line 252
# parameter: self — line 252
# variable: telemetry — line 254
# variable: span — line 261
# variable: started — line 262
# variable: status — line 263
# definition: forward — line 278
# parameter: self — line 278
# variable: span — line 285
# variable: context — line 286
# variable: header — line 287
# variable: connection — line 288
# variable: response — line 293
# variable: body — line 294
# variable: status — line 295
# variable: status — line 301
# definition: Lab — line 309
# definition: __init__ — line 312
# parameter: self — line 313
# parameter: output — line 314
# parameter: faults — line 315
# parameter: gateway_port — line 316
# parameter: worker_port — line 317
# variable: worker_telemetry — line 325
# variable: worker — line 327
# variable: gateway_telemetry — line 329
# variable: gateway — line 331
# definition: gateway_port — line 340
# parameter: self — line 340
# definition: __enter__ — line 344
# parameter: self — line 344
# variable: server — line 346
# variable: thread — line 347
# definition: __exit__ — line 354
# parameter: args — line 354
# parameter: self — line 354
# definition: close — line 358
# parameter: self — line 358
# variable: server — line 360
# variable: thread — line 362
# variable: server — line 364
# variable: telemetry — line 366
# END CODE MAP

from __future__ import annotations

import http.client
import json
import socket
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from opentelemetry.trace import SpanKind, Status, StatusCode

from sre.slo import integer
from sre.telemetry import Telemetry, parent_context


@dataclass(frozen=True)
class Faults:
    """Worker-only bounded fault schedule; settings cannot be changed through an HTTP request."""

    every: int = 0
    until: int = 0
    delay_ms: int = 0

    def __post_init__(self) -> None:
        """Reject unbounded faults; every=0 means never fail, until caps the affected attempt range."""
        integer(self.every, 0, 100)
        integer(self.until, 0, 1000)
        integer(self.delay_ms, 0, 100)


class Server(ThreadingHTTPServer):
    """Loopback-only HTTP server with at most 16 concurrent request handlers and a socket deadline."""

    daemon_threads = False
    block_on_close = True
    request_queue_size = 16
    # Windows SO_REUSEADDR can permit duplicate binds; never share a lab listener.
    allow_reuse_address = False

    def __init__(
        self, telemetry: Telemetry, faults: Faults, upstream: int | None, port: int = 0
    ) -> None:
        """Bind 127.0.0.1 only; attach validated telemetry, worker schedule, upstream port and semaphore."""
        integer(port, 0, 65535)
        if upstream is not None:
            integer(upstream, 1, 65535)
        self.telemetry = telemetry
        self.faults = faults
        self.upstream = upstream
        self.count = 0
        self.count_lock = threading.Lock()
        self.slots = threading.BoundedSemaphore(16)
        super().__init__(("127.0.0.1", port), Handler)

    def process_request(
        self, request: socket.socket | tuple[bytes, socket.socket], client_address: Any
    ) -> None:
        """Reject excess concurrent connections without spawning an unbounded thread."""
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(
        self, request: socket.socket | tuple[bytes, socket.socket], client_address: Any
    ) -> None:
        """Always release the concurrency slot even when parsing or request handling fails."""
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()

    def next_status(self) -> int:
        """Increment the worker attempt index atomically and apply the fixed finite fault schedule."""
        with self.count_lock:
            self.count += 1
            fail = (
                self.faults.every > 0
                and self.count <= self.faults.until
                and self.count % self.faults.every == 0
            )
        time.sleep(self.faults.delay_ms / 1000)
        return 503 if fail else 200


class Handler(BaseHTTPRequestHandler):
    """Closed endpoint contract; never log/echo raw request content, headers or query strings."""

    server: Server

    def setup(self) -> None:
        """Limit socket lifetime for slow headers/body clients before invoking the standard parser."""
        self.request.settimeout(1.0)
        super().setup()

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress the standard raw HTTP request logger to prevent accidental user-data retention."""

    def send_error(
        self, code: int, message: str | None = None, explain: str | None = None
    ) -> None:
        """Use a fixed error body instead of reflecting a request method or parser-supplied message."""
        self.reply(code, b'{"error":"request rejected"}')

    def reply(
        self, status: int, body: bytes, content_type: str = "application/json"
    ) -> None:
        """Send fixed content with no caching/sniffing; tolerate a peer that disconnected on timeout."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.send_header(
            "Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'"
        )
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self) -> None:
        """Serve only exact health/metrics/work routes; reject bodies, transfer encoding and queries."""
        if (
            self.headers.get("Content-Length", "0") != "0"
            or "Transfer-Encoding" in self.headers
        ):
            self.reply(400, b'{"error":"body not allowed"}')
        elif self.path == "/health":
            self.reply(
                200,
                json.dumps(
                    {
                        "lab": "sre-observability-workbench",
                        "service": self.server.telemetry.service,
                    }
                ).encode(),
            )
        elif self.path == "/metrics":
            self.reply(
                200,
                self.server.telemetry.metrics(),
                "text/plain; version=0.0.4; charset=utf-8",
            )
        elif self.path == "/work":
            self.work()
        else:
            self.reply(404, b'{"error":"route not found"}')

    def work(self) -> None:
        """Measure one completed work call and propagate only the validated W3C trace context upstream."""
        telemetry = self.server.telemetry
        with telemetry.tracer.start_as_current_span(
            "work",
            context=parent_context(self.headers.get("traceparent")),
            kind=SpanKind.SERVER,
            record_exception=False,
            set_status_on_exception=False,
        ) as span:
            started = time.perf_counter()
            status = (
                self.server.next_status()
                if self.server.upstream is None
                else self.forward()
            )
            if status >= 500:
                span.set_status(Status(StatusCode.ERROR))
            telemetry.observe(status, time.perf_counter() - started)
            self.reply(
                status,
                b'{"result":"synthetic work"}'
                if status == 200
                else b'{"error":"synthetic unavailable"}',
            )

    def forward(self) -> int:
        """Call the fixed loopback worker with a deadline; ignore raw bodies and never follow redirects."""
        with self.server.telemetry.tracer.start_as_current_span(
            "worker.call",
            kind=SpanKind.CLIENT,
            record_exception=False,
            set_status_on_exception=False,
        ) as span:
            context = span.get_span_context()
            header = f"00-{context.trace_id:032x}-{context.span_id:016x}-01"
            connection = http.client.HTTPConnection(
                "127.0.0.1", self.server.upstream, timeout=0.5
            )
            try:
                connection.request("GET", "/work", headers={"traceparent": header})
                response = connection.getresponse()
                body = response.read(1025)
                status = (
                    response.status
                    if response.status in (200, 503) and len(body) <= 1024
                    else 502
                )
            except (OSError, http.client.HTTPException):
                status = 502
            finally:
                connection.close()
            if status >= 500:
                span.set_status(Status(StatusCode.ERROR))
            return status


class Lab:
    """Own two servers and evidence files; scope all fault injection to newly created local resources."""

    def __init__(
        self,
        output: Path,
        faults: Faults | None = None,
        gateway_port: int = 0,
        worker_port: int = 0,
    ) -> None:
        """Create a new private output directory and services; roll back owned resources on partial startup."""
        output.mkdir(mode=0o700, parents=True, exist_ok=False)
        self.servers: list[Server] = []
        self.telemetry: list[Telemetry] = []
        self.threads: list[threading.Thread] = []
        try:
            worker_telemetry = Telemetry("worker", output)
            self.telemetry.append(worker_telemetry)
            worker = Server(worker_telemetry, faults or Faults(), None, worker_port)
            self.servers.append(worker)
            gateway_telemetry = Telemetry("gateway", output)
            self.telemetry.append(gateway_telemetry)
            gateway = Server(
                gateway_telemetry, Faults(), worker.server_port, gateway_port
            )
            self.servers.append(gateway)
        except BaseException:
            self.close()
            raise

    @property
    def gateway_port(self) -> int:
        """Return the actual bound gateway port, including OS-assigned ephemeral ports."""
        return self.servers[1].server_port

    def __enter__(self) -> Lab:
        """Start owned server loops; return this lab for bounded requests and automatic cleanup."""
        for server in self.servers:
            thread = threading.Thread(
                target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
            )
            thread.start()
            self.threads.append(thread)
        return self

    def __exit__(self, *args: object) -> None:
        """Stop and join every owned service regardless of client success or failure."""
        self.close()

    def close(self) -> None:
        """Close only owned sockets/providers; wait for bounded active handlers before closing their files."""
        for server in self.servers[: len(self.threads)]:
            server.shutdown()
        for thread in self.threads:
            thread.join(timeout=3)
        for server in self.servers:
            server.server_close()
        for telemetry in self.telemetry:
            telemetry.close()
        self.servers.clear()
        self.threads.clear()
        self.telemetry.clear()

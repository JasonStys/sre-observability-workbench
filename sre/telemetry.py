"""Allowlisted local OpenTelemetry spans, correlated logs and bounded Prometheus labels. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: parent_context — line 60
# parameter: header — line 60
# variable: parts — line 63
# definition: LocalExporter — line 69
# definition: __init__ — line 72
# parameter: path — line 72
# parameter: self — line 72
# definition: export — line 78
# parameter: self — line 78
# parameter: spans — line 78
# variable: span — line 81
# variable: context — line 84
# variable: service — line 87
# variable: record — line 90
# definition: shutdown — line 107
# parameter: self — line 107
# definition: Telemetry — line 113
# definition: __init__ — line 116
# parameter: output — line 116
# parameter: self — line 116
# parameter: service — line 116
# variable: group — line 137
# definition: observe — line 153
# parameter: elapsed — line 153
# parameter: self — line 153
# parameter: status — line 153
# variable: group — line 155
# variable: context — line 158
# variable: record — line 159
# definition: metrics — line 173
# parameter: self — line 173
# definition: close — line 177
# parameter: self — line 177
# END CODE MAP

from __future__ import annotations

import json
import re
import threading
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest


def parent_context(header: str | None) -> Context:
    """Accept only valid version-00 traceparent; discard baggage, tracestate, raw URLs and headers."""
    if header and re.fullmatch(r"00-[0-9a-f]{32}-[0-9a-f]{16}-0[01]", header):
        parts = header.split("-")
        if int(parts[1], 16) and int(parts[2], 16):
            return TraceContextTextMapPropagator().extract({"traceparent": header})
    return Context()


class LocalExporter(SpanExporter):
    """Export a capped set of sanitized span records to an exclusively created local JSONL file."""

    def __init__(self, path: Path) -> None:
        """Create path once; keep lock and export counter private to this exporter."""
        self.stream = path.open("x", encoding="utf-8")
        self.lock = threading.Lock()
        self.count = 0

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Persist fixed fields for each span under a lock; never serialize arbitrary attributes/events."""
        with self.lock:
            for span in spans:
                if self.count >= 10_000:
                    return SpanExportResult.FAILURE
                context = span.get_span_context()
                if context is None:
                    return SpanExportResult.FAILURE
                service = (span.resource.attributes or {}).get(
                    "service.name", "unknown"
                )
                record = {
                    "service": service,
                    "name": span.name,
                    "trace_id": format(context.trace_id, "032x"),
                    "span_id": format(context.span_id, "016x"),
                    "parent_id": format(span.parent.span_id, "016x")
                    if span.parent
                    else None,
                    "status": span.status.status_code.name,
                    "start_ns": span.start_time,
                    "end_ns": span.end_time,
                }
                self.stream.write(json.dumps(record, sort_keys=True) + "\n")
                self.count += 1
            self.stream.flush()
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        """Close the owned evidence stream after the server has stopped handling requests."""
        with self.lock:
            self.stream.close()


class Telemetry:
    """Service-owned provider, registry and private structured log; no global or external exporter."""

    def __init__(self, service: str, output: Path) -> None:
        """Initialize gateway/worker metrics with bounded labels and SDK spans in the new output directory."""
        from opentelemetry.sdk.resources import Resource

        if service not in {"gateway", "worker"}:
            raise ValueError("unknown lab service")
        self.service = service
        self.registry = CollectorRegistry()
        self.requests = Counter(
            "workbench_requests_total",
            "Completed work attempts",
            ["service", "status_group"],
            registry=self.registry,
        )
        self.duration = Histogram(
            "workbench_request_duration_seconds",
            "Work attempt duration",
            ["service", "status_group"],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 1.0),
            registry=self.registry,
        )
        for group in ("2xx", "4xx", "5xx"):
            self.requests.labels(service, group)
            self.duration.labels(service, group)
        self.provider = TracerProvider(
            sampler=ALWAYS_ON,
            resource=Resource.create({"service.name": service}),
            shutdown_on_exit=False,
        )
        self.provider.add_span_processor(
            SimpleSpanProcessor(LocalExporter(output / f"{service}-spans.jsonl"))
        )
        self.tracer = self.provider.get_tracer("sre.workbench", "1.0.0")
        self.log_stream = (output / f"{service}-logs.jsonl").open("x", encoding="utf-8")
        self.lock = threading.Lock()
        self.log_count = 0

    def observe(self, status: int, elapsed: float) -> None:
        """Record one fixed-operation work attempt; include failures in both metric denominators."""
        group = f"{status // 100}xx"
        self.requests.labels(self.service, group).inc()
        self.duration.labels(self.service, group).observe(elapsed)
        context = trace.get_current_span().get_span_context()
        record: dict[str, Any] = {
            "service": self.service,
            "operation": "work",
            "status": status,
            "duration_us": round(elapsed * 1_000_000),
            "trace_id": format(context.trace_id, "032x"),
            "span_id": format(context.span_id, "016x"),
        }
        with self.lock:
            if self.log_count < 10_000:
                self.log_stream.write(json.dumps(record, sort_keys=True) + "\n")
                self.log_stream.flush()
                self.log_count += 1

    def metrics(self) -> bytes:
        """Serialize only this service's registry; health/scrape requests are not business traffic."""
        return generate_latest(self.registry)

    def close(self) -> None:
        """Shut down the SDK and owned log handle after all active work threads have joined."""
        self.provider.shutdown()
        self.log_stream.close()

"""Validate client evidence and calculate exact request-based SLOs. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: MAX_EVENTS — line 104
# variable: MAX_BYTES — line 105
# variable: FIELDS — line 106
# definition: integer — line 109
# parameter: maximum — line 109
# parameter: minimum — line 109
# parameter: value — line 109
# definition: identifier — line 116
# parameter: size — line 116
# parameter: value — line 116
# definition: Event — line 128
# variable: id — line 131
# variable: at_ms — line 132
# variable: duration_us — line 133
# variable: status — line 134
# variable: trace_id — line 135
# variable: span_id — line 136
# definition: parse — line 139
# parameter: cls — line 139
# parameter: raw — line 139
# variable: status — line 145
# definition: Policy — line 159
# variable: target_ppm — line 162
# variable: latency_us — line 163
# variable: window_ms — line 164
# variable: min_requests — line 165
# definition: __post_init__ — line 167
# parameter: self — line 167
# definition: unique_object — line 175
# parameter: pairs — line 175
# variable: result — line 177
# variable: key — line 178
# variable: value — line 178
# definition: load_events — line 185
# parameter: path — line 185
# variable: stream — line 187
# variable: content — line 188
# definition: parse_events — line 192
# parameter: content — line 192
# variable: events — line 194
# variable: seen — line 195
# variable: line — line 198
# variable: event — line 201
# definition: stats — line 209
# parameter: events — line 209
# parameter: latency — line 209
# parameter: policy — line 209
# variable: count — line 211
# variable: bad — line 212
# variable: event — line 217
# variable: allowed — line 219
# variable: burn — line 220
# definition: pair_state — line 231
# parameter: events — line 232
# parameter: policy — line 233
# parameter: as_of_ms — line 234
# parameter: long_ms — line 235
# parameter: short_ms — line 236
# parameter: threshold — line 237
# parameter: latency — line 238
# variable: burns — line 241
# variable: window — line 242
# variable: selected — line 243
# variable: event — line 244
# variable: bad — line 248
# variable: event — line 253
# variable: burn — line 258
# definition: assess — line 261
# parameter: events — line 262
# parameter: policy — line 263
# parameter: as_of_ms — line 264
# parameter: expected_events — line 265
# variable: event — line 269
# variable: selected — line 273
# variable: event — line 275
# variable: event — line 278
# variable: future — line 278
# variable: complete — line 279
# variable: durations — line 282
# variable: event — line 282
# variable: percentiles — line 283
# variable: percent — line 287
# variable: result — line 289
# variable: event — line 302
# variable: event — line 303
# variable: latency — line 306
# variable: name — line 306
# variable: fast — line 307
# variable: slow — line 310
# variable: alert — line 313
# END CODE MAP

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

MAX_EVENTS = 10_000
MAX_BYTES = 8 * 1024 * 1024
FIELDS = {"schema", "id", "at_ms", "duration_us", "status", "trace_id", "span_id"}


def integer(value: object, minimum: int, maximum: int) -> int:
    """Require a bounded integer, excluding bool and coercible strings; return the validated value."""
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError("expected bounded integer")
    return value


def identifier(value: object, size: int) -> str:
    """Require a nonzero lower-case hex trace/span identifier of exactly size characters."""
    if (
        not isinstance(value, str)
        or not re.fullmatch(rf"[0-9a-f]{{{size}}}", value)
        or int(value, 16) == 0
    ):
        raise ValueError("invalid trace identifier")
    return value


@dataclass(frozen=True)
class Event:
    """One completed client attempt: UTC finish time, monotonic duration and bounded correlation IDs."""

    id: int
    at_ms: int
    duration_us: int
    status: int
    trace_id: str
    span_id: str

    @classmethod
    def parse(cls, raw: object) -> Event:
        """Validate a versioned closed record; raw must contain every field and no extra user data."""
        if not isinstance(raw, dict) or set(raw) != FIELDS:
            raise ValueError("event fields do not match schema 1")
        if type(raw["schema"]) is not int or raw["schema"] != 1:
            raise ValueError("unsupported event schema")
        status = integer(raw["status"], 0, 599)
        if status != 0 and status < 100:
            raise ValueError("invalid HTTP status")
        return cls(
            integer(raw["id"], 1, MAX_EVENTS),
            integer(raw["at_ms"], 0, 4_102_444_800_000),
            integer(raw["duration_us"], 0, 10_000_000),
            status,
            identifier(raw["trace_id"], 32),
            identifier(raw["span_id"], 16),
        )


@dataclass(frozen=True)
class Policy:
    """Request-based objective with exact parts-per-million target, latency threshold and volume floor."""

    target_ppm: int = 999_000
    latency_us: int = 50_000
    window_ms: int = 30 * 24 * 60 * 60 * 1000
    min_requests: int = 20

    def __post_init__(self) -> None:
        """Reject invalid bounds and a 100% target whose burn rate would divide by zero."""
        integer(self.target_ppm, 1, 999_999)
        integer(self.latency_us, 1, 10_000_000)
        integer(self.window_ms, 1, 31 * 24 * 60 * 60 * 1000)
        integer(self.min_requests, 1, MAX_EVENTS)


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject ambiguous duplicate JSON keys instead of silently accepting the last value."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def load_events(path: Path) -> list[Event]:
    """Read bounded UTF-8 JSONL, reject duplicate attempts and return events without executing content."""
    with path.open("rb") as stream:
        content = stream.read(MAX_BYTES + 1)
    return parse_events(content)


def parse_events(content: bytes) -> list[Event]:
    """Validate one bounded byte snapshot so reports can hash exactly the evidence they assess."""
    events: list[Event] = []
    seen: set[int] = set()
    if len(content) > MAX_BYTES:
        raise ValueError("evidence exceeds byte cap")
    for line in content.decode("utf-8").splitlines():
        if not line.strip():
            raise ValueError("blank evidence line")
        event = Event.parse(json.loads(line, object_pairs_hook=unique_object))
        if event.id in seen or len(events) >= MAX_EVENTS:
            raise ValueError("duplicate attempt or event cap exceeded")
        seen.add(event.id)
        events.append(event)
    return events


def stats(events: list[Event], policy: Policy, latency: bool = False) -> dict[str, Any]:
    """Calculate exact bad counts/burn; latency successes must also have successful HTTP status."""
    count = len(events)
    bad = sum(
        not (
            200 <= event.status < 300
            and (not latency or event.duration_us <= policy.latency_us)
        )
        for event in events
    )
    allowed = Fraction(count * (1_000_000 - policy.target_ppm), 1_000_000)
    burn = Fraction(bad, 1) / allowed if count else None
    return {
        "requests": count,
        "bad": bad,
        "good_ratio": float(Fraction(count - bad, count)) if count else None,
        "allowed_bad": float(allowed),
        "budget_remaining": float(allowed - bad),
        "burn_rate": float(burn) if burn is not None else None,
    }


def pair_state(
    events: list[Event],
    policy: Policy,
    as_of_ms: int,
    long_ms: int,
    short_ms: int,
    threshold: Fraction,
    latency: bool,
) -> str:
    """Use strict burn comparison in both trailing windows; insufficient volume is never CLEAR."""
    burns = []
    for window in (long_ms, short_ms):
        selected = [
            event for event in events if as_of_ms - window < event.at_ms <= as_of_ms
        ]
        if len(selected) < policy.min_requests:
            return "INSUFFICIENT_DATA"
        bad = sum(
            not (
                200 <= event.status < 300
                and (not latency or event.duration_us <= policy.latency_us)
            )
            for event in selected
        )
        burns.append(
            Fraction(bad * 1_000_000, len(selected) * (1_000_000 - policy.target_ppm))
        )
    return "PAGE" if all(burn > threshold for burn in burns) else "CLEAR"


def assess(
    events: list[Event],
    policy: Policy,
    as_of_ms: int,
    expected_events: int | None = None,
) -> dict[str, Any]:
    """Summarize a bounded evidence window and two independent SLIs without declaring missing data healthy."""
    integer(as_of_ms, 0, 4_102_444_800_000)
    if len(events) > MAX_EVENTS or len({event.id for event in events}) != len(events):
        raise ValueError("invalid evidence count or duplicate ID")
    if expected_events is not None:
        integer(expected_events, 0, MAX_EVENTS)
    selected = [
        event
        for event in events
        if as_of_ms - policy.window_ms < event.at_ms <= as_of_ms
    ]
    future = sum(event.at_ms > as_of_ms for event in events)
    complete = (
        expected_events is not None and expected_events == len(selected) and future == 0
    )
    durations = sorted(event.duration_us for event in selected)
    percentiles = {
        f"p{percent}_us": durations[(percent * len(durations) + 99) // 100 - 1]
        if durations
        else None
        for percent in (50, 95, 99)
    }
    result: dict[str, Any] = {
        "schema": 1,
        "synthetic": True,
        "as_of_ms": as_of_ms,
        "policy": {
            "target_ppm": policy.target_ppm,
            "latency_us": policy.latency_us,
            "window_ms": policy.window_ms,
            "min_requests": policy.min_requests,
        },
        "quality": "COMPLETE_ASSERTED" if complete else "INSUFFICIENT_DATA",
        "expected_events": expected_events,
        "future_events": future,
        "observed_span_ms": max((event.at_ms for event in selected), default=as_of_ms)
        - min((event.at_ms for event in selected), default=as_of_ms),
        "percentiles": percentiles,
    }
    for name, latency in (("availability", False), ("latency", True)):
        fast = pair_state(
            events, policy, as_of_ms, 3_600_000, 300_000, Fraction(72, 5), latency
        )
        slow = pair_state(
            events, policy, as_of_ms, 21_600_000, 1_800_000, Fraction(6), latency
        )
        alert = (
            "PAGE"
            if "PAGE" in (fast, slow)
            else "CLEAR"
            if fast == slow == "CLEAR"
            else "INSUFFICIENT_DATA"
        )
        result[name] = {
            **stats(selected, policy, latency),
            "fast_pair": fast,
            "slow_pair": slow,
            "alert": alert if complete else "INSUFFICIENT_DATA",
        }
    return result

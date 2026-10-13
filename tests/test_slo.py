"""Exact SLO algebra, boundary, schema and adversarial evidence tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: event — line 71
# parameter: duration — line 72
# parameter: index — line 72
# parameter: status — line 72
# parameter: timestamp — line 72
# definition: test_integer_rejects_coercions — line 79
# parameter: value — line 79
# definition: test_id_rejects_invalid — line 86
# parameter: value — line 86
# definition: test_event_schema — line 105
# parameter: changes — line 105
# variable: raw — line 107
# definition: test_invalid_policy — line 125
# parameter: policy — line 125
# definition: test_windows_missing_and_future — line 131
# variable: events — line 133
# variable: report — line 134
# variable: report — line 139
# definition: test_latency_and_exact_threshold — line 150
# variable: events — line 152
# variable: index — line 153
# variable: policy — line 155
# variable: index — line 169
# definition: test_percentiles_and_recovery — line 178
# variable: report — line 180
# variable: index — line 181
# variable: index — line 191
# variable: old — line 191
# variable: healthy — line 192
# variable: index — line 192
# variable: report — line 193
# definition: test_budget_algebra — line 199
# parameter: outcomes — line 199
# variable: events — line 201
# variable: good — line 203
# variable: index — line 203
# variable: report — line 205
# variable: expected — line 206
# definition: test_evidence_reader — line 214
# parameter: tmp_path — line 214
# variable: path — line 216
# variable: raw — line 217
# variable: content — line 220
# END CODE MAP

from __future__ import annotations

import json
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from sre.slo import (
    Event,
    Policy,
    assess,
    identifier,
    integer,
    load_events,
    pair_state,
    stats,
)


def event(
    index: int = 1, timestamp: int = 10_000_000, status: int = 200, duration: int = 1000
) -> Event:
    """Create only fictional bounded client evidence; index also gives nonzero deterministic IDs."""
    return Event(index, timestamp, duration, status, f"{index:032x}", f"{index:016x}")


@pytest.mark.parametrize("value", [True, False, -1, 11, 1.2, "1", None])
def test_integer_rejects_coercions(value: object) -> None:
    """Bool/string/float/unbounded input must not silently enter exact integer arithmetic."""
    with pytest.raises(ValueError):
        integer(value, 0, 10)


@pytest.mark.parametrize("value", ["0" * 32, "A" * 32, "1" * 31, None, "<script>" * 4])
def test_id_rejects_invalid(value: object) -> None:
    """Trace correlation fields are closed nonzero lowercase hexadecimal strings."""
    with pytest.raises(ValueError):
        identifier(value, 32)


@pytest.mark.parametrize(
    "changes",
    [
        {"schema": 2},
        {"schema": True},
        {"status": 99},
        {"status": 600},
        {"id": 0},
        {"duration_us": -1},
        {"trace_id": "0" * 32},
        {"extra": "private"},
    ],
)
def test_event_schema(changes: dict[str, object]) -> None:
    """A versioned closed schema prevents ambiguous fields, raw payloads and malformed measurements."""
    raw = {"schema": 1, **asdict(event())}
    with pytest.raises(ValueError):
        Event.parse({**raw, **changes})
    assert Event.parse(raw) == event()
    assert Event.parse({**raw, "status": 0}).status == 0
    with pytest.raises(ValueError):
        Event.parse([])


@pytest.mark.parametrize(
    "policy",
    [
        {"target_ppm": 1_000_000},
        {"latency_us": 0},
        {"window_ms": 0},
        {"min_requests": 0},
    ],
)
def test_invalid_policy(policy: dict[str, int]) -> None:
    """Reject division-by-zero objectives and invalid latency/window/volume settings."""
    with pytest.raises(ValueError):
        Policy(**policy)


def test_windows_missing_and_future() -> None:
    """Trailing windows exclude their left endpoint, include their right endpoint and flag missing records."""
    events = [event(1, 999), event(2, 1000), event(3, 2000), event(4, 2001)]
    report = assess(events, Policy(window_ms=1000), 2000, 1)
    assert report["availability"]["requests"] == 1
    assert report["future_events"] == 1
    assert report["quality"] == "INSUFFICIENT_DATA"
    assert report["availability"]["alert"] == "INSUFFICIENT_DATA"
    report = assess(events[:3], Policy(window_ms=1000), 2000, 1)
    assert report["quality"] == "COMPLETE_ASSERTED"
    assert report["availability"]["alert"] == "INSUFFICIENT_DATA"
    assert assess([], Policy(), 2000, 0)["availability"]["good_ratio"] is None
    assert assess([event()], Policy(), 10_000_000)["quality"] == "INSUFFICIENT_DATA"
    with pytest.raises(ValueError):
        assess([event(), event()], Policy(), 10_000_000, 2)
    with pytest.raises(ValueError):
        assess([], Policy(), 1, -1)


def test_latency_and_exact_threshold() -> None:
    """Fast failures never count as good latency; a burn exactly on threshold does not page."""
    events = [
        event(index, status=503 if index <= 9 else 200) for index in range(1, 626)
    ]
    policy = Policy(min_requests=1)
    assert (
        pair_state(
            events, policy, 10_000_000, 3_600_000, 300_000, Fraction(72, 5), False
        )
        == "CLEAR"
    )
    events[9] = event(10, status=503)
    assert assess(events, policy, 10_000_000, 625)["availability"]["alert"] == "PAGE"
    assert stats([event(status=503, duration=1)], policy, True)["bad"] == 1
    assert stats([event(duration=50_000)], policy, True)["bad"] == 0
    assert stats([event(duration=50_001)], policy, True)["bad"] == 1
    assert (
        assess(
            [event(index, duration=60_000) for index in range(1, 21)],
            Policy(),
            10_000_000,
            20,
        )["latency"]["alert"]
        == "PAGE"
    )


def test_percentiles_and_recovery() -> None:
    """Nearest-rank percentiles include failures; aged failures must leave both burn windows before CLEAR."""
    report = assess(
        [event(index, duration=index * 1000) for index in range(1, 101)],
        Policy(),
        10_000_000,
        100,
    )
    assert report["percentiles"] == {
        "p50_us": 50_000,
        "p95_us": 95_000,
        "p99_us": 99_000,
    }
    old = [event(index, 1000, 503) for index in range(1, 21)]
    healthy = [event(index, 25_000_000) for index in range(21, 41)]
    report = assess(old + healthy, Policy(window_ms=3_600_000), 25_000_000, 20)
    assert report["availability"]["alert"] == "CLEAR"


@given(st.lists(st.booleans(), min_size=1, max_size=200))
@settings(max_examples=150, deadline=None)
def test_budget_algebra(outcomes: list[bool]) -> None:
    """Across randomized outcome batches the exact burn and observed budget agree with their rational formula."""
    events = [
        event(index + 1, status=200 if good else 503)
        for index, good in enumerate(outcomes)
    ]
    report = assess(events, Policy(min_requests=1), 10_000_000, len(events))
    expected = Fraction(outcomes.count(False) * 1000, len(outcomes))
    assert report["availability"]["burn_rate"] == float(expected)
    assert report["availability"]["bad"] == outcomes.count(False)
    assert report == assess(
        list(reversed(events)), Policy(min_requests=1), 10_000_000, len(events)
    )


def test_evidence_reader(tmp_path: Path) -> None:
    """UTF-8 JSONL accepts valid bounded evidence, rejecting duplicate keys/IDs and malformed records."""
    path = tmp_path / "events.jsonl"
    raw = json.dumps({"schema": 1, **asdict(event())})
    path.write_text(raw + "\n", encoding="utf-8")
    assert load_events(path) == [event()]
    for content in [
        raw + "\n" + raw,
        "\n",
        '{"schema":1,"schema":1}',
        "not JSON",
        "x" * (8 * 1024 * 1024 + 1),
    ]:
        path.write_text(content, encoding="utf-8")
        with pytest.raises(ValueError):
            load_events(path)
    path.write_bytes(b"\xff")
    with pytest.raises(UnicodeError):
        load_events(path)

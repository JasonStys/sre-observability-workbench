"""Independent service/journey comparison and operator workflow checks. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: POLICY — line 64
# definition: fixture — line 72
# parameter: tmp_path — line 72
# variable: streams — line 74
# variable: name — line 75
# variable: events — line 76
# variable: number — line 86
# variable: event — line 89
# variable: manifest — line 102
# variable: path — line 103
# definition: test_independent_journeys_and_thresholds — line 108
# parameter: tmp_path — line 108
# variable: _ — line 110
# variable: path — line 110
# variable: result — line 111
# variable: checkout — line 112
# variable: inventory — line 112
# definition: test_missing_evidence_and_looser_target_not_improvement — line 129
# parameter: tmp_path — line 129
# variable: data — line 131
# variable: path — line 131
# variable: result — line 135
# definition: test_ambiguous_manifest_refused — line 162
# parameter: bad — line 162
# parameter: tmp_path — line 162
# variable: data — line 164
# variable: path — line 164
# variable: row — line 165
# definition: test_user_cli_inert_output_and_no_overwrite — line 191
# parameter: tmp_path — line 191
# variable: data — line 193
# variable: path — line 193
# variable: original — line 196
# variable: argv — line 197
# variable: page — line 202
# variable: result — line 205
# definition: test_missing_and_oversized_sources — line 211
# parameter: tmp_path — line 211
# variable: _ — line 213
# variable: path — line 213
# definition: test_aggregate_bounds_and_demo — line 219
# parameter: monkeypatch — line 220
# parameter: tmp_path — line 220
# variable: output — line 225
# variable: path — line 227
# variable: result — line 228
# variable: stream — line 229
# variable: stream — line 234
# variable: name — line 246
# END CODE MAP

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from sre.__main__ import main
from sre.bundle import analyze, publish

POLICY = {
    "target_ppm": 999000,
    "latency_us": 50000,
    "window_ms": 2592000000,
    "min_requests": 20,
}


def fixture(tmp_path: Path) -> tuple[Path, dict[str, object]]:
    """Create independent checkout and inventory streams with deliberately different failure patterns."""
    streams = []
    for name in ("checkout", "inventory"):
        events = [
            {
                "schema": 1,
                "id": number,
                "at_ms": 1000000,
                "duration_us": 80000 if name == "checkout" and number <= 2 else 1000,
                "status": 503 if name == "inventory" and number == 1 else 200,
                "trace_id": f"{number:032x}",
                "span_id": f"{number:016x}",
            }
            for number in range(1, 21)
        ]
        (tmp_path / f"{name}.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in events)
        )
        streams.append(
            {
                "service": "retail",
                "journey": name,
                "owner": "Store reliability",
                "events": f"{name}.jsonl",
                "expected_events": 20,
                "baseline_policy": POLICY.copy(),
                "candidate_policy": {**POLICY, "latency_us": 100000},
            }
        )
    manifest: dict[str, object] = {"schema": 1, "as_of_ms": 1000000, "streams": streams}
    path = tmp_path / "bundle.json"
    path.write_text(json.dumps(manifest))
    return path, manifest


def test_independent_journeys_and_thresholds(tmp_path: Path) -> None:
    """A slower allowed threshold clears latency pages but cannot erase inventory HTTP failures."""
    path, _ = fixture(tmp_path)
    result = analyze(path)
    checkout, inventory = result["streams"]
    assert result["total_input_events"] == 40
    assert checkout["baseline"]["latency"]["bad"] == 2
    assert checkout["candidate"]["latency"]["bad"] == 0
    assert checkout["changes"]["latency"]["baseline_alert"] == "PAGE"
    assert checkout["changes"]["latency"]["candidate_alert"] == "CLEAR"
    assert checkout["changes"]["latency"]["bad_delta"] == -2
    assert checkout["loosened_thresholds"] == ["latency_us"]
    assert inventory["candidate"]["availability"]["bad"] == 1
    assert inventory["candidate"]["availability"]["alert"] == "PAGE"
    assert (
        checkout["evidence_sha256"]
        == hashlib.sha256((tmp_path / "checkout.jsonl").read_bytes()).hexdigest()
    )
    assert result["review_queue"][0]["reasons"] == ["objective_loosened"]


def test_missing_evidence_and_looser_target_not_improvement(tmp_path: Path) -> None:
    """Quality never improves just by lowering targets, and each stream has its own denominator."""
    path, data = fixture(tmp_path)
    data["streams"][0]["expected_events"] = 21
    data["streams"][0]["candidate_policy"]["target_ppm"] = 990000
    path.write_text(json.dumps(data))
    result = analyze(path)
    assert result["streams"][0]["candidate"]["quality"] == "INSUFFICIENT_DATA"
    assert (
        result["streams"][0]["candidate"]["availability"]["alert"]
        == "INSUFFICIENT_DATA"
    )
    assert result["streams"][1]["candidate"]["quality"] == "COMPLETE_ASSERTED"
    assert "evidence_incomplete" in result["review_queue"][0]["reasons"]
    assert result["streams"][0]["loosened_thresholds"] == ["target_ppm", "latency_us"]


@pytest.mark.parametrize(
    "bad",
    [
        "schema",
        "count",
        "duplicate",
        "file-reuse",
        "path",
        "bad-policy",
        "window",
        "volume",
        "owner",
        "expected",
        "unknown",
    ],
)
def test_ambiguous_manifest_refused(tmp_path: Path, bad: str) -> None:
    """Scope, bounds and settings cannot silently change which attempts an objective compares."""
    path, data = fixture(tmp_path)
    row = data["streams"][0]
    if bad == "schema":
        data["schema"] = True
    elif bad == "count":
        data["streams"] = []
    elif bad == "duplicate":
        data["streams"].append(row)
    elif bad == "file-reuse":
        data["streams"][1]["events"] = row["events"]
    elif bad == "path":
        row["events"] = "../outside.jsonl"
    elif bad == "bad-policy":
        row["candidate_policy"]["target_ppm"] = 1000000
    elif bad in ("window", "volume"):
        row["candidate_policy"]["window_ms" if bad == "window" else "min_requests"] = 1
    elif bad == "owner":
        row["owner"] = "\n"
    elif bad == "expected":
        row["expected_events"] = True
    else:
        row["extra"] = "ignored?"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        analyze(path)


def test_user_cli_inert_output_and_no_overwrite(tmp_path: Path) -> None:
    """The actual CLI opens a local comparison report without changing source telemetry or policies."""
    path, data = fixture(tmp_path)
    data["streams"][0]["owner"] = "<script>no()</script>"
    path.write_text(json.dumps(data))
    original = path.read_bytes()
    argv = ["sre", "bundle", str(path), "--output", str(tmp_path / "review")]
    with patch("sys.argv", argv):
        assert main() == 0
        assert main() == 2
    assert path.read_bytes() == original
    page = (tmp_path / "review/journeys.html").read_text()
    assert "<script>" not in page and "&lt;script&gt;" in page
    assert "Content-Security-Policy" in page and "Jason Stys" in page
    result = json.loads((tmp_path / "review/journeys.json").read_text())
    assert result["stream_count"] == 2
    with pytest.raises(OSError):
        publish(result, tmp_path / "absent/new")


def test_missing_and_oversized_sources(tmp_path: Path) -> None:
    """Manifest and aggregate evidence bounds stop reads before unbounded input is accumulated."""
    path, _ = fixture(tmp_path)
    (tmp_path / "checkout.jsonl").unlink()
    with pytest.raises(ValueError):
        analyze(path)


def test_aggregate_bounds_and_demo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An independent generated demo has the expected failure counts; aggregate caps cover all journeys."""
    from scripts.journey_demo import generate

    output = tmp_path / "demo"
    generate(output)
    path = output / "bundle.json"
    result = analyze(path)
    assert [stream["baseline"]["latency"]["bad"] for stream in result["streams"]] == [
        2,
        1,
    ]
    assert [
        stream["candidate"]["availability"]["bad"] for stream in result["streams"]
    ] == [0, 1]
    with pytest.raises(OSError):
        generate(output)
    monkeypatch.setattr("sre.bundle.MAX_EVENTS", 20)
    with pytest.raises(ValueError, match="event bound"):
        analyze(path)
    monkeypatch.setattr("sre.bundle.MAX_EVENTS", 10000)
    monkeypatch.setattr(
        "sre.bundle.MAX_BYTES",
        max(
            (output / name).stat().st_size
            for name in ("checkout.jsonl", "warehouse.jsonl")
        )
        + 1,
    )
    with pytest.raises(ValueError, match="byte bound"):
        analyze(path)
    path.write_bytes(b" " * 262145)
    with pytest.raises(ValueError):
        analyze(path)

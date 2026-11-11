"""Independent native SLO/journey oracles and actual owned-service failure/retention boundaries. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: state — line 102
# parameter: tmp_path — line 102
# variable: value — line 104
# definition: run — line 109
# parameter: changes — line 109
# parameter: scenario — line 109
# parameter: state — line 109
# parameter: tmp_path — line 109
# variable: parameters — line 111
# variable: stage — line 112
# variable: files — line 114
# variable: kind — line 114
# variable: summary — line 114
# variable: identity — line 115
# definition: test_owned_actual_fault_recovery_chains_and_complete_jsonl — line 119
# parameter: state — line 119
# parameter: tmp_path — line 119
# variable: files — line 121
# variable: views — line 121
# variable: evidence — line 122
# variable: report — line 122
# variable: events — line 135
# variable: event — line 137
# variable: event — line 139
# definition: test_custom_evidence_independent_latency_counts_and_missing_denominator — line 144
# parameter: state — line 145
# parameter: tmp_path — line 145
# variable: files — line 148
# variable: views — line 148
# variable: report — line 149
# variable: original — line 153
# variable: _ — line 154
# variable: files — line 154
# definition: test_disjoint_journeys_and_same_evidence_threshold_tradeoff — line 159
# parameter: state — line 159
# parameter: tmp_path — line 159
# variable: files — line 161
# variable: views — line 161
# variable: result — line 162
# variable: indexed — line 165
# variable: row — line 165
# variable: row — line 169
# variable: _ — line 170
# variable: files — line 170
# variable: compared — line 171
# definition: test_invalid_settings_do_not_publish_or_substitute_samples — line 193
# parameter: field — line 194
# parameter: state — line 194
# parameter: tmp_path — line 194
# parameter: value — line 194
# definition: test_comparison_requires_explicit_count_and_valid_input_modes — line 202
# parameter: state — line 202
# parameter: tmp_path — line 202
# variable: parameters — line 207
# variable: bad — line 212
# definition: test_deadline_exposes_unattempted_work_without_fabricated_success — line 218
# parameter: monkeypatch — line 219
# parameter: tmp_path — line 219
# variable: clock — line 222
# variable: _ — line 226
# variable: events — line 226
# variable: result — line 226
# definition: test_client_failure_kept_with_explicit_service_evidence_gap — line 235
# parameter: monkeypatch — line 235
# parameter: tmp_path — line 235
# variable: seen — line 237
# definition: FailedConnection — line 239
# definition: __init__ — line 242
# parameter: host — line 242
# parameter: port — line 242
# parameter: self — line 242
# parameter: timeout — line 242
# definition: request — line 246
# parameter: headers — line 246
# parameter: method — line 246
# parameter: path — line 246
# parameter: self — line 246
# definition: close — line 253
# parameter: self — line 253
# variable: _ — line 265
# variable: events — line 265
# variable: result — line 265
# definition: test_literal_cell_fields_do_not_interpret_labels — line 271
# variable: row — line 273
# END CODE MAP

from types import SimpleNamespace

import pytest

from sre import desktop_drill
from sre import desktop_project as project
from sre.desktop_io import Rejected, json_value
from sre.desktop_state import Workspace
from sre.service import Faults
from sre.slo import parse_events


@pytest.fixture
def state(tmp_path):
    """Use only an owned isolated local database, never the default application profile."""
    value = Workspace(tmp_path / "profile", project.PRODUCT, project.ROOT)
    yield value
    value.close()


def run(state, tmp_path, scenario, **changes):
    """Call the real adapter and retain only complete results, as the actual native worker does."""
    parameters = {**project.scenario(project.SCENARIOS[scenario]), **changes}
    stage = tmp_path / f"stage-{len(state.history())}"
    stage.mkdir()
    kind, summary, files = project.analyze(state, parameters, stage)
    identity = state.save(kind, summary, parameters, files)
    return files, project.views(state.files(identity))


def test_owned_actual_fault_recovery_chains_and_complete_jsonl(state, tmp_path):
    """Forty real requests must retain four finite failures, 120 actual spans and 80 logs with exact chains."""
    files, views = run(state, tmp_path, 0)
    report, evidence = (
        json_value(files["assessment.json"]),
        json_value(files["drill.json"]),
    )
    assert (
        report["availability"]["requests"] == 40 and report["availability"]["bad"] == 4
    )
    assert (
        report["availability"]["alert"] == "PAGE"
        and report["quality"] == "COMPLETE_ASSERTED"
    )
    assert evidence["service_spans"] == 120 and evidence["service_logs"] == 80
    assert evidence["correlated_attempts"] == 40 and evidence["evidence_gaps"] == []
    events = parse_events(files["events.jsonl"])
    assert len(events) == 40 and [
        event.id for event in events if event.status == 503
    ] == [3, 6, 9, 12]
    assert all(event.status == 200 for event in events[12:])
    assert len(files) == 8 and len(views["Real service spans"]) == 120
    assert project.cells(views["Availability and latency"][0])[-1] == "PAGE"


def test_custom_evidence_independent_latency_counts_and_missing_denominator(
    state, tmp_path
):
    """Checkout has only two slow successes; an omitted completeness assertion must remain insufficient."""
    files, views = run(state, tmp_path, 1)
    report = json_value(files["assessment.json"])
    assert report["availability"]["bad"] == 0 and report["latency"]["bad"] == 2
    assert report["percentiles"] == {"p50_us": 1000, "p95_us": 80000, "p99_us": 80000}
    assert len(views["Actual request attempts"]) == 20
    original = state.files(1)
    files, _ = run(state, tmp_path, 1, expected_events="")
    assert json_value(files["assessment.json"])["quality"] == "INSUFFICIENT_DATA"
    assert state.files(1) == original


def test_disjoint_journeys_and_same_evidence_threshold_tradeoff(state, tmp_path):
    """Two independent streams retain their own owner; loosening latency is never measured operational recovery."""
    files, views = run(state, tmp_path, 2)
    result = json_value(files["journeys.json"])
    assert result["stream_count"] == 2 and result["total_input_events"] == 40
    assert len(views["Owner review queue"]) == 2
    indexed = {row["journey"]: row for row in result["streams"]}
    assert indexed["checkout"]["baseline"]["latency"]["bad"] == 2
    assert indexed["warehouse"]["baseline"]["availability"]["bad"] == 1
    assert indexed["checkout"]["owner"] == "Payments reliability"
    assert all("objective_loosened" in row["reasons"] for row in result["review_queue"])
    files, _ = run(state, tmp_path, 3)
    compared = json_value(files["journeys.json"])["streams"][0]
    assert (
        compared["baseline"]["latency"]["bad"] == 2
        and compared["candidate"]["latency"]["bad"] == 0
    )
    assert compared["loosened_thresholds"] == ["latency_us"]
    assert parse_events(files["events.jsonl"])[0].id == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("attempts", "51"),
        ("attempts", "0"),
        ("target_ppm", "1000000"),
        ("latency_us", "NaN"),
        ("fault_every", "1.5"),
        ("delay_ms", "101"),
        ("target_ppm", "-1"),
        ("target_ppm", "1" * 17),
    ],
)
def test_invalid_settings_do_not_publish_or_substitute_samples(
    state, tmp_path, field, value
):
    """Bad units and bounds cannot become a default objective, new saved report or unbounded traffic schedule."""
    with pytest.raises((Rejected, ValueError)):
        run(state, tmp_path, 0, **{field: value})
    assert state.history() == []


def test_comparison_requires_explicit_count_and_valid_input_modes(state, tmp_path):
    """An evidence completeness assertion cannot be invented to make a candidate objective look better."""
    with pytest.raises(Rejected, match="expected count"):
        run(state, tmp_path, 3, expected_events="")
    assert state.history() == []
    parameters = project.scenario(project.SCENARIOS[1])
    with pytest.raises(Rejected):
        project.scenario("unknown")
    with pytest.raises(Rejected):
        project.analyze(state, {**parameters, "mode": "unknown"}, tmp_path)
    bad = tmp_path / "malformed.jsonl"
    bad.write_text('{"schema":1}')
    with pytest.raises(ValueError):
        project.analyze(state, {**parameters, "events": str(bad)}, tmp_path)


def test_deadline_exposes_unattempted_work_without_fabricated_success(
    tmp_path, monkeypatch
):
    """A bounded schedule stops new requests but leaves the expected denominator and missing work explicit."""
    clock = iter([0, 16])
    monkeypatch.setattr(
        desktop_drill, "time", SimpleNamespace(monotonic=lambda: next(clock))
    )
    events, result, _ = desktop_drill.drill(tmp_path, 2, Faults())
    assert (
        events == []
        and result["requested_attempts"] == 2
        and result["completed_attempts"] == 0
    )
    assert result["deadline_exhausted"] is True and result["correlated_attempts"] == 0


def test_client_failure_kept_with_explicit_service_evidence_gap(tmp_path, monkeypatch):
    """A failed client connection is status0/bad, not a successful fallback or a silently omitted attempt."""
    seen = []

    class FailedConnection:
        """Fault only the new client's transport; existing Lab still owns real isolated listener lifetimes."""

        def __init__(self, host, port, timeout):
            """Record the fixed owned destination; no user target is accepted."""
            seen.append((host, port, timeout))

        def request(self, method, path, headers):
            """Expose a genuine transport-failure result to the client's retention branch."""
            assert (
                method == "GET" and path == "/work" and set(headers) == {"traceparent"}
            )
            raise OSError("Synthetic client transport unavailable")

        def close(self):
            """The owned inert transport has no OS resource."""

    monkeypatch.setattr(
        desktop_drill,
        "http",
        SimpleNamespace(
            client=SimpleNamespace(
                HTTPConnection=FailedConnection, HTTPException=RuntimeError
            )
        ),
    )
    events, result, _ = desktop_drill.drill(tmp_path, 1, Faults())
    assert len(events) == 1 and events[0].status == 0
    assert result["failures"] == 1 and result["correlated_attempts"] == 0
    assert len(result["evidence_gaps"]) == 1 and seen[0][0] == "127.0.0.1"


def test_literal_cell_fields_do_not_interpret_labels():
    """Selected evidence remains ordinary text, including hostile-looking labels and unavailable signals."""
    row = {
        "service": "<script>fictional</script>",
        "journey": "checkout",
        "reasons": ["objective_loosened"],
        "signal": "latency",
    }
    assert project.cells(row) == (
        "<script>fictional</script> / checkout",
        "latency",
        "objective_loosened",
        "REVIEW",
    )

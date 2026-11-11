"""Independent service/journey objectives and same-evidence policy review. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: fields — line 93
# parameter: names — line 93
# parameter: raw — line 93
# definition: label — line 100
# parameter: raw — line 100
# variable: c — line 105
# definition: regular — line 111
# parameter: limit — line 111
# parameter: path — line 111
# variable: part — line 116
# variable: descriptor — line 121
# variable: stream — line 124
# variable: content — line 127
# definition: analyze — line 133
# parameter: path — line 133
# variable: content — line 135
# variable: manifest — line 136
# variable: clock — line 141
# variable: reports — line 147
# variable: queue — line 148
# variable: seen — line 149
# variable: sources — line 150
# variable: total_bytes — line 151
# variable: total_events — line 151
# variable: raw — line 152
# variable: row — line 153
# variable: journey — line 165
# variable: owner — line 165
# variable: service — line 165
# variable: key — line 166
# variable: identity — line 168
# variable: filename — line 172
# variable: source — line 182
# variable: event_bytes — line 183
# variable: total_bytes — line 184
# variable: events — line 187
# variable: total_events — line 188
# variable: expected — line 191
# variable: policies — line 192
# variable: key — line 193
# variable: settings — line 194
# variable: baseline — line 198
# variable: candidate — line 198
# variable: before — line 206
# variable: after — line 207
# variable: loosened — line 208
# variable: changes — line 213
# variable: name — line 221
# variable: reasons — line 223
# variable: name — line 226
# variable: name — line 230
# variable: stream — line 235
# parameter: item — line 264
# parameter: item — line 266
# definition: publish — line 272
# parameter: output — line 272
# parameter: result — line 272
# variable: absolute — line 274
# variable: part — line 277
# variable: text — line 280
# variable: rows — line 281
# variable: stream — line 282
# variable: values — line 283
# variable: name — line 291
# variable: value — line 296
# variable: page — line 299
# END CODE MAP

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import stat
from pathlib import Path
from typing import Any

from sre.slo import (
    MAX_BYTES,
    MAX_EVENTS,
    Policy,
    assess,
    integer,
    parse_events,
    unique_object,
)


def fields(raw: object, names: set[str]) -> dict[str, Any]:
    """Require a closed object; reject misspelled settings rather than silently ignoring them."""
    if not isinstance(raw, dict) or set(raw) != names:
        raise ValueError("bundle object fields do not match contract")
    return raw


def label(raw: object) -> str:
    """Validate a bounded service/journey/team label without interpreting markup or terminal escapes."""
    if (
        not isinstance(raw, str)
        or not 1 <= len(raw) <= 120
        or any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in raw)
    ):
        raise ValueError("invalid bundle label")
    return raw


def regular(path: Path, limit: int) -> bytes:
    """Read an existing bounded local regular file with no symlink/junction ancestors."""
    if (
        any(
            part.is_symlink() or part.is_junction()
            for part in (path.absolute(), *path.absolute().parents)
        )
        or not path.is_file()
    ):
        raise ValueError("bundle input must be an unlinked regular file")
    descriptor = os.open(
        path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    )
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("bundle input changed to a non-regular descriptor")
        content = stream.read(limit + 1)
    if len(content) > limit:
        raise ValueError("bundle input exceeds byte bound")
    return content


def analyze(path: Path) -> dict[str, Any]:
    """Assess <=20 disjoint declared journeys, then compare thresholds on identical evidence/windows."""
    content = regular(path, 262144)
    manifest = fields(
        json.loads(content, object_pairs_hook=unique_object),
        {"schema", "as_of_ms", "streams"},
    )
    integer(manifest["schema"], 1, 1)
    clock = integer(manifest["as_of_ms"], 0, 4_102_444_800_000)
    if (
        not isinstance(manifest["streams"], list)
        or not 1 <= len(manifest["streams"]) <= 20
    ):
        raise ValueError("bundle needs 1..20 streams")
    reports = []
    queue = []
    seen = set()
    sources = set()
    total_events = total_bytes = 0
    for raw in manifest["streams"]:
        row = fields(
            raw,
            {
                "service",
                "journey",
                "owner",
                "events",
                "expected_events",
                "baseline_policy",
                "candidate_policy",
            },
        )
        service, journey, owner = (
            label(row[key]) for key in ("service", "journey", "owner")
        )
        identity = (service, journey)
        if identity in seen:
            raise ValueError("duplicate service/journey")
        seen.add(identity)
        filename = label(row["events"])
        # Manifest references are deliberately one local filename: no arbitrary paths or URLs.
        if (
            not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,119}\.jsonl", filename)
            or ".." in filename
        ):
            raise ValueError("events must be a local JSONL filename")
        if filename in sources:
            raise ValueError("journeys must have distinct evidence files")
        sources.add(filename)
        source = path.parent / filename
        event_bytes = regular(source, MAX_BYTES)
        total_bytes += len(event_bytes)
        if total_bytes > MAX_BYTES:
            raise ValueError("bundle evidence byte bound exceeded")
        events = parse_events(event_bytes)
        total_events += len(events)
        if total_events > MAX_EVENTS:
            raise ValueError("bundle event bound exceeded")
        expected = integer(row["expected_events"], 0, MAX_EVENTS)
        policies = []
        for key in ("baseline_policy", "candidate_policy"):
            settings = fields(
                row[key], {"target_ppm", "latency_us", "window_ms", "min_requests"}
            )
            policies.append(Policy(**settings))
        baseline, candidate = policies
        if (
            baseline.window_ms != candidate.window_ms
            or baseline.min_requests != candidate.min_requests
        ):
            raise ValueError(
                "threshold comparison requires identical window and volume floor"
            )
        before = assess(events, baseline, clock, expected)
        after = assess(events, candidate, clock, expected)
        loosened = []
        if candidate.target_ppm < baseline.target_ppm:
            loosened.append("target_ppm")
        if candidate.latency_us > baseline.latency_us:
            loosened.append("latency_us")
        changes = {
            name: {
                "baseline_alert": before[name]["alert"],
                "candidate_alert": after[name]["alert"],
                "bad_delta": after[name]["bad"] - before[name]["bad"],
                "budget_remaining_delta": after[name]["budget_remaining"]
                - before[name]["budget_remaining"],
            }
            for name in ("availability", "latency")
        }
        reasons = []
        if after["quality"] != "COMPLETE_ASSERTED":
            reasons.append("evidence_incomplete")
        if any(after[name]["alert"] == "PAGE" for name in ("availability", "latency")):
            reasons.append("candidate_burn_page")
        if any(
            after[name]["alert"] == "INSUFFICIENT_DATA"
            for name in ("availability", "latency")
        ):
            reasons.append("insufficient_window_volume")
        if loosened:
            reasons.append("objective_loosened")
        stream = {
            "service": service,
            "journey": journey,
            "owner": owner,
            "evidence_file": filename,
            "evidence_sha256": hashlib.sha256(event_bytes).hexdigest(),
            "baseline": before,
            "candidate": after,
            "changes": changes,
            "loosened_thresholds": loosened,
        }
        reports.append(stream)
        if reasons:
            queue.append(
                {
                    "service": service,
                    "journey": journey,
                    "owner": owner,
                    "reasons": reasons,
                }
            )
    return {
        "schema": 1,
        "kind": "journey_threshold_review",
        "synthetic": True,
        "manifest_sha256": hashlib.sha256(content).hexdigest(),
        "as_of_ms": clock,
        "stream_count": len(reports),
        "total_input_events": total_events,
        "streams": sorted(reports, key=lambda item: (item["service"], item["journey"])),
        "review_queue": sorted(
            queue, key=lambda item: (item["service"], item["journey"])
        ),
        "scope": "Independent synthetic streams; no pooled availability, automatic policy approval or PromQL/dashboard rewrite.",
    }


def publish(result: dict[str, Any], output: Path) -> None:
    """Create immutable local JSON/HTML with a visible journey comparison and escaped detail."""
    absolute = output.absolute()
    if any(
        part.is_symlink() or part.is_junction()
        for part in (absolute, *absolute.parents)
    ):
        raise ValueError("output traverses a link")
    text = json.dumps(result, sort_keys=True, indent=2, allow_nan=False)
    rows = []
    for stream in result["streams"]:
        values = [
            stream["service"],
            stream["journey"],
            stream["owner"],
            stream["candidate"]["quality"],
        ]
        values.extend(
            f"{stream[name]['availability']['alert']} / {stream[name]['latency']['alert']}"
            for name in ("baseline", "candidate")
        )
        values.append(", ".join(stream["loosened_thresholds"]) or "none")
        rows.append(
            "<tr>"
            + "".join(f"<td>{html.escape(str(value))}</td>" for value in values)
            + "</tr>"
        )
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; base-uri 'none'; form-action 'none'\">"
        "<title>Journey SLO review — Jason Stys</title><main><h1>Service and journey objective review</h1>"
        "<p>Created by Jason Stys. Same evidence and clock, independent journeys; completeness is asserted.</p>"
        "<table><caption>Availability / latency alert comparison</caption><thead><tr><th>Service</th><th>Journey</th><th>Owner</th><th>Evidence</th><th>Baseline</th><th>Candidate</th><th>Loosened thresholds</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table><details><summary>Full results, hashes and owner review queue</summary><pre>"
        + html.escape(text)
        + "</pre></details><p>Review objective changes with stakeholders. This is not approval or a production reliability claim.</p></main></html>"
    )
    absolute.mkdir(mode=0o700, exist_ok=False)
    (absolute / "journeys.json").write_text(text + "\n", encoding="utf-8")
    (absolute / "journeys.html").write_text(page, encoding="utf-8")

"""Publish inert escaped HTML, JSON and parameterized SQLite evidence. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 24
# definition: publish — line 27
# parameter: events — line 27
# parameter: output — line 27
# parameter: result — line 27
# variable: text — line 30
# variable: page — line 32
# variable: connection — line 38
# variable: event — line 52
# END CODE MAP

from __future__ import annotations

import html
import json
import sqlite3
from pathlib import Path
from typing import Any

from sre.slo import Event

ROOT = Path(__file__).resolve().parents[1]


def publish(result: dict[str, Any], events: list[Event], output: Path) -> None:
    """Create new output only; render escaped fixed-format evidence without JS/assets/external requests."""
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    text = json.dumps(result, indent=2, sort_keys=True, allow_nan=False)
    (output / "assessment.json").write_text(text + "\n", encoding="utf-8")
    page = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; base-uri \'none\'; form-action \'none\'"><title>SRE evidence — Jason Stys</title><body><h1>SRE Observability Workbench</h1><p>Created by Jason Stys · github.com/JasonStys · LinkedIn: jason-stys-31b30b351</p><p>Synthetic local drill evidence; not a production availability claim. COMPLETE_ASSERTED relies on the supplied expected count, not cryptographic provenance.</p><h2>Measured assessment</h2><pre>'
        + html.escape(text)
        + "</pre><p>Help: README and docs/runbook.md in the repository.</p></body></html>"
    )
    (output / "assessment.html").write_text(page, encoding="utf-8")
    connection = sqlite3.connect(output / "evidence.db")
    try:
        connection.executescript((ROOT / "ops/schema.sql").read_text(encoding="utf-8"))
        connection.executemany(
            "INSERT INTO attempts VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    event.id,
                    event.at_ms,
                    event.duration_us,
                    event.status,
                    event.trace_id,
                    event.span_id,
                )
                for event in events
            ],
        )
        connection.execute("INSERT INTO reports(payload) VALUES (?)", (text,))
        connection.commit()
    finally:
        connection.close()

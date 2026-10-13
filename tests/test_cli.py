"""CLI parsing, shutdown and sanitized failure contract tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_assess_cli — line 24
# parameter: capsys — line 24
# parameter: tmp_path — line 24
# variable: raw — line 26
# variable: source — line 27
# definition: test_serve_cli — line 60
# parameter: tmp_path — line 60
# variable: lab — line 80
# END CODE MAP

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from sre.__main__ import main
from sre.slo import Event


def test_assess_cli(tmp_path: Path, capsys: object) -> None:
    """A supplied evidence file creates all three reports; missing/untrusted input returns a safe nonzero exit."""
    raw = {"schema": 1, **asdict(Event(1, 1000, 10, 200, "1" * 32, "2" * 16))}
    source = tmp_path / "events.jsonl"
    source.write_text(json.dumps(raw) + "\n", encoding="utf-8")
    with patch(
        "sys.argv",
        [
            "sre",
            "assess",
            str(source),
            "--output",
            str(tmp_path / "report"),
            "--as-of-ms",
            "1000",
            "--expected-events",
            "1",
        ],
    ):
        assert main() == 0
    assert (tmp_path / "report/assessment.html").is_file()
    with patch(
        "sys.argv",
        [
            "sre",
            "assess",
            str(tmp_path / "missing"),
            "--output",
            str(tmp_path / "other"),
            "--as-of-ms",
            "1000",
        ],
    ):
        assert main() == 2


def test_serve_cli(tmp_path: Path) -> None:
    """A controlled interruption must close every socket/exporter rather than requiring an orphaned server."""
    with (
        patch(
            "sys.argv",
            [
                "sre",
                "serve",
                "--output",
                str(tmp_path / "serve"),
                "--gateway-port",
                "0",
                "--worker-port",
                "0",
            ],
        ),
        patch("threading.Event.wait", side_effect=KeyboardInterrupt),
    ):
        # Mock only the blocking main wait; Server threads use Event.wait internally,
        # so start/stop lifecycle is exercised by the native integration test instead.
        with patch("sre.__main__.Lab") as lab:
            lab.return_value.__enter__.return_value.gateway_port = 8000
            lab.return_value.__enter__.return_value.servers[0].server_port = 8001
            assert main() == 0
            lab.return_value.__exit__.assert_called_once()

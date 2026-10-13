"""Measure bounded SLO analysis, not service capacity or asymptotic proof. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 32
# definition: measure — line 38
# variable: events — line 40
# variable: index — line 49
# variable: samples — line 51
# variable: _ — line 52
# variable: started — line 53
# variable: result — line 54
# variable: _ — line 60
# variable: peak — line 60
# variable: sample — line 66
# definition: main — line 74
# variable: parser — line 76
# variable: arguments — line 78
# variable: result — line 79
# variable: stream — line 82
# END CODE MAP

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sre.slo import Event, Policy, assess  # noqa: E402


def measure() -> dict[str, object]:
    """Analyze 10,000 fictional attempts five times and report median wall time plus Python allocation peak."""
    events = [
        Event(
            index,
            10_000_000 - index,
            1000,
            503 if index % 100 == 0 else 200,
            f"{index:032x}",
            f"{index:016x}",
        )
        for index in range(1, 10_001)
    ]
    samples = []
    for _ in range(5):
        started = time.perf_counter()
        result = assess(events, Policy(), 10_000_000, len(events))
        samples.append((time.perf_counter() - started) * 1000)
        if result["availability"]["bad"] != 100:
            raise ValueError("benchmark correctness mismatch")
    tracemalloc.start()
    assess(events, Policy(), 10_000_000, len(events))
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "events": len(events),
        "repetitions": 5,
        "median_ms": round(statistics.median(samples), 3),
        "samples_ms": [round(sample, 3) for sample in samples],
        "peak_python_allocated_bytes": peak,
        "python": platform.python_version(),
        "os": platform.system(),
        "scope": "in-memory SLO analyzer only; timings are informational, no machine-dependent hard latency gate",
    }


def main() -> int:
    """Print actual measured evidence or exclusively create an explicitly requested JSON output file."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = json.dumps(measure(), indent=2, sort_keys=True)
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        with arguments.output.open("x", encoding="utf-8") as stream:
            stream.write(result + "\n")
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Create a finite fictional retail checkout/warehouse journey bundle. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: generate — line 21
# parameter: output — line 21
# variable: streams — line 24
# variable: policy — line 25
# variable: journey — line 31
# variable: owner — line 31
# variable: events — line 35
# variable: number — line 45
# variable: event — line 48
# definition: main — line 68
# variable: parser — line 70
# END CODE MAP

import argparse
import json
from pathlib import Path


def generate(output: Path) -> None:
    """Create synthetic local inputs only; do not start servers, send requests or alter existing output."""
    output.mkdir(mode=0o700, exist_ok=False)
    streams = []
    policy = {
        "target_ppm": 999000,
        "latency_us": 50000,
        "window_ms": 2592000000,
        "min_requests": 20,
    }
    for journey, owner in (
        ("checkout", "Payments reliability"),
        ("warehouse", "Inventory reliability"),
    ):
        events = [
            {
                "schema": 1,
                "id": number,
                "at_ms": 1000000,
                "duration_us": 80000 if journey == "checkout" and number <= 2 else 1000,
                "status": 503 if journey == "warehouse" and number == 1 else 200,
                "trace_id": f"{number:032x}",
                "span_id": f"{number:016x}",
            }
            for number in range(1, 21)
        ]
        (output / f"{journey}.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in events), encoding="utf-8"
        )
        streams.append(
            {
                "service": "fictional-retail",
                "journey": journey,
                "owner": owner,
                "events": f"{journey}.jsonl",
                "expected_events": 20,
                "baseline_policy": policy,
                "candidate_policy": {**policy, "latency_us": 100000},
            }
        )
    (output / "bundle.json").write_text(
        json.dumps({"schema": 1, "as_of_ms": 1000000, "streams": streams}, indent=2)
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    """Parse one new destination and create the public-safe fictional inputs."""
    parser = argparse.ArgumentParser(
        description="Jason Stys — synthetic journey inputs"
    )
    parser.add_argument("--output", type=Path, required=True)
    generate(parser.parse_args().output)


if __name__ == "__main__":
    main()

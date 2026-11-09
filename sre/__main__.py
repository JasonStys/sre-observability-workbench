"""Local-only service and evidence-assessment command line. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: main — line 29
# variable: parser — line 31
# variable: subcommands — line 34
# variable: serve — line 35
# variable: analyze — line 42
# variable: journeys — line 49
# variable: arguments — line 54
# variable: lab — line 64
# variable: comparison — line 80
# variable: events — line 91
# variable: result — line 92
# END CODE MAP

from __future__ import annotations

import argparse
import json
import threading
from pathlib import Path

from sre import bundle
from sre.report import publish
from sre.service import Faults, Lab
from sre.slo import Policy, assess, load_events


def main() -> int:
    """Parse explicit bounded settings, keep evidence local and never echo untrusted input on failure."""
    parser = argparse.ArgumentParser(
        description="SRE Observability Workbench — Jason Stys"
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    serve = subcommands.add_parser("serve")
    serve.add_argument("--output", type=Path, required=True)
    serve.add_argument("--gateway-port", type=int, default=8000)
    serve.add_argument("--worker-port", type=int, default=8001)
    serve.add_argument("--fault-every", type=int, default=0)
    serve.add_argument("--fault-until", type=int, default=0)
    serve.add_argument("--delay-ms", type=int, default=0)
    analyze = subcommands.add_parser("assess")
    analyze.add_argument("events", type=Path)
    analyze.add_argument("--output", type=Path, required=True)
    analyze.add_argument("--as-of-ms", type=int, required=True)
    analyze.add_argument("--expected-events", type=int)
    analyze.add_argument("--target-ppm", type=int, default=999_000)
    analyze.add_argument("--latency-us", type=int, default=50_000)
    journeys = subcommands.add_parser(
        "bundle", help="Compare independent service/journey objectives"
    )
    journeys.add_argument("manifest", type=Path)
    journeys.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    try:
        if arguments.command == "serve":
            with Lab(
                arguments.output,
                Faults(
                    arguments.fault_every, arguments.fault_until, arguments.delay_ms
                ),
                arguments.gateway_port,
                arguments.worker_port,
            ) as lab:
                print(
                    json.dumps(
                        {
                            "gateway_port": lab.gateway_port,
                            "worker_port": lab.servers[0].server_port,
                            "author": "Jason Stys",
                        }
                    ),
                    flush=True,
                )
                try:
                    threading.Event().wait()
                except KeyboardInterrupt:
                    pass
        elif arguments.command == "bundle":
            comparison = bundle.analyze(arguments.manifest)
            bundle.publish(comparison, arguments.output)
            print(
                json.dumps(
                    {
                        "streams": comparison["stream_count"],
                        "review_items": len(comparison["review_queue"]),
                    }
                )
            )
        else:
            events = load_events(arguments.events)
            result = assess(
                events,
                Policy(
                    target_ppm=arguments.target_ppm, latency_us=arguments.latency_us
                ),
                arguments.as_of_ms,
                arguments.expected_events,
            )
            publish(result, events, arguments.output)
            print(
                json.dumps(
                    {
                        "quality": result["quality"],
                        "availability_alert": result["availability"]["alert"],
                    }
                )
            )
    except (OSError, ValueError, UnicodeError, RecursionError):
        print(
            "Input/output rejected; consult docs/runbook.md for the bounded local contract."
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Fail on unsafe telemetry/configuration metadata or undocumented dashboard drift. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 29
# definition: validate — line 32
# variable: dashboard — line 34
# variable: ids — line 43
# variable: panel — line 43
# variable: panel — line 46
# variable: target — line 47
# variable: datasource — line 50
# variable: config — line 61
# variable: target — line 64
# variable: path — line 67
# variable: workflow — line 69
# variable: job — line 72
# variable: step — line 73
# variable: action — line 74
# variable: word — line 80
# END CODE MAP

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def validate() -> None:
    """Check closed synthetic deployment conventions, pinned actions, metrics labels and account-free storage."""
    dashboard = json.loads(
        (ROOT / "ops/grafana/dashboard.json").read_text(encoding="utf-8")
    )
    if (
        len(dashboard["panels"]) != 7
        or dashboard["editable"]
        or "Jason Stys" not in dashboard["title"]
    ):
        raise ValueError("reviewed dashboard contract changed")
    ids = [panel["id"] for panel in dashboard["panels"]]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate dashboard panel ID")
    for panel in dashboard["panels"]:
        for target in panel.get("targets", []):
            if not target["expr"] or "trace_id" in target["expr"]:
                raise ValueError("unbounded dashboard label")
    datasource = yaml.safe_load(
        (ROOT / "ops/grafana/provisioning/datasources/default.yml").read_text(
            encoding="utf-8"
        )
    )["datasources"][0]
    if (
        datasource["url"] != "http://127.0.0.1:9090"
        or datasource["editable"]
        or "secureJsonData" in datasource
    ):
        raise ValueError("datasource must stay local and credential-free")
    config = yaml.safe_load((ROOT / "ops/prometheus.yml").read_text(encoding="utf-8"))
    if set(config) != {"global", "rule_files", "scrape_configs"}:
        raise ValueError("unexpected telemetry exporter/configuration")
    for target in config["scrape_configs"][0]["static_configs"][0]["targets"]:
        if not re.fullmatch(r"127\.0\.0\.1:[0-9]{1,5}", target):
            raise ValueError("scrape target must remain local")
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        # BaseLoader preserves the workflow 'on' key rather than YAML 1.1 boolean coercion.
        workflow = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        if "pull_request_target" in workflow["on"]:
            raise ValueError("privileged PR execution is forbidden")
        for job in workflow["jobs"].values():
            for step in job["steps"]:
                action = step.get("uses", "")
                if action and not re.fullmatch(
                    r"[A-Za-z0-9_./-]+@[0-9a-f]{40}", action
                ):
                    raise ValueError("action must use a complete commit pin")
                if any(
                    word in action for word in ("upload-artifact", "/cache@")
                ) or step.get("with", {}).get("cache"):
                    raise ValueError("lab must not add Actions artifact/cache storage")
    print(
        "Dashboard, local telemetry and storage-free pinned workflow contracts passed"
    )


if __name__ == "__main__":
    validate()

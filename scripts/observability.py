"""Validate real Prometheus scraping and an optional disposable CI-only Grafana dashboard. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 67
# definition: read_api — line 73
# parameter: authorization — line 73
# parameter: path — line 73
# parameter: port — line 73
# variable: request — line 75
# variable: response — line 81
# variable: data — line 82
# variable: result — line 85
# definition: query — line 91
# parameter: expression — line 91
# variable: result — line 93
# definition: wait_for — line 101
# parameter: check — line 101
# parameter: description — line 101
# variable: deadline — line 103
# variable: value — line 106
# definition: validate — line 115
# parameter: grafana — line 115
# parameter: output — line 115
# variable: binary — line 123
# variable: node — line 128
# variable: container — line 132
# variable: started_container — line 133
# variable: report — line 134
# variable: lab — line 135
# variable: config — line 136
# variable: server — line 142
# variable: config_path — line 144
# variable: log — line 146
# variable: process — line 147
# variable: counts — line 181
# variable: errors — line 195
# variable: password — line 215
# variable: environment — line 216
# variable: image — line 217
# variable: started_container — line 267
# variable: authorization — line 268
# variable: dashboard — line 272
# variable: health — line 285
# variable: data — line 292
# definition: main — line 347
# variable: parser — line 349
# variable: arguments — line 352
# END CODE MAP

from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sre.service import Faults, Lab  # noqa: E402


def read_api(port: int, path: str, authorization: str | None = None) -> dict[str, Any]:
    """Read capped JSON only from a fixed owned loopback service; keep authorization out of logs."""
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        headers={"Authorization": authorization} if authorization else {},
    )
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(
        request, timeout=2
    ) as response:
        data = response.read(256 * 1024 + 1)
    if len(data) > 256 * 1024:
        raise ValueError("API response cap")
    result = json.loads(data)
    if not isinstance(result, dict):
        raise ValueError("API object required")
    return result


def query(expression: str) -> list[dict[str, Any]]:
    """Query the fixed owned Prometheus instance; no arbitrary remote query endpoint is accepted."""
    result = read_api(
        9090, "/api/v1/query?" + urllib.parse.urlencode({"query": expression})
    )
    if result.get("status") != "success":
        raise ValueError("Prometheus query failed")
    return list(result["data"]["result"])


def wait_for(check: Any, description: str) -> Any:
    """Poll a concrete owned readiness condition for at most 30 seconds without masking its final failure."""
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        try:
            value = check()
            if value:
                return value
        except (OSError, ValueError, KeyError):
            pass
        time.sleep(0.2)
    raise ValueError(f"owned service not ready: {description}")


def validate(output: Path, grafana: bool = False) -> dict[str, Any]:
    """Start only owned synthetic services/tools, prove actual scrapes/querying, and always remove the CI container."""
    if grafana and (
        sys.platform != "linux" or os.environ.get("GITHUB_ACTIONS") != "true"
    ):
        raise ValueError(
            "Grafana container validation is restricted to disposable Linux Actions runners"
        )
    binary = (
        ROOT
        / ".tools"
        / ("prometheus.exe" if sys.platform == "win32" else "prometheus")
    )
    node = shutil.which("node")
    if not binary.is_file() or node is None:
        raise ValueError("install verified Prometheus and build the Node client first")
    output.mkdir(parents=True, mode=0o700, exist_ok=False)
    container = "sre-workbench-" + secrets.token_hex(6)
    started_container = False
    report: dict[str, Any] = {"synthetic": True, "prometheus_version": "3.15.0"}
    with Lab(output / "services", Faults(3, 12)) as lab:
        config = yaml.safe_load(
            (ROOT / "ops/prometheus.yml").read_text(encoding="utf-8")
        )
        config["global"] = {"scrape_interval": "1s", "evaluation_interval": "1s"}
        config["rule_files"] = [str(ROOT / "ops/rules.yml")]
        config["scrape_configs"][0]["static_configs"][0]["targets"] = [
            f"127.0.0.1:{server.server_port}" for server in lab.servers
        ]
        config_path = output / "prometheus.yml"
        config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
        with (output / "prometheus.log").open("x", encoding="utf-8") as log:
            process = subprocess.Popen(
                [
                    str(binary),
                    "--config.file=" + str(config_path),
                    "--storage.tsdb.path=" + str(output / "tsdb"),
                    "--storage.tsdb.retention.time=1h",
                    "--web.listen-address=127.0.0.1:9090",
                ],
                stdout=log,
                stderr=log,
            )
            try:
                wait_for(
                    lambda: (
                        process.poll() is None
                        and len(query('up{job="workbench"} == 1')) == 2
                    ),
                    "two successful service scrapes",
                )
                subprocess.run(
                    [
                        node,
                        str(ROOT / "dist/load.js"),
                        "--target",
                        f"http://127.0.0.1:{lab.gateway_port}",
                        "--output",
                        str(output / "client"),
                        "--attempts",
                        "40",
                        "--ack-owned-target",
                    ],
                    check=True,
                    timeout=120,
                )
                counts = wait_for(
                    lambda: (
                        query('sum(workbench_requests_total{service="gateway"})')
                        if query('sum(workbench_requests_total{service="gateway"})')
                        and float(
                            query('sum(workbench_requests_total{service="gateway"})')[
                                0
                            ]["value"][1]
                        )
                        == 40
                        else False
                    ),
                    "40 scraped gateway attempts",
                )
                errors = query(
                    'sum(workbench_requests_total{service="gateway",status_group="5xx"})'
                )
                if float(errors[0]["value"][1]) != 4:
                    raise ValueError(
                        "Prometheus error count disagrees with controlled drill"
                    )
                wait_for(
                    lambda: query("workbench:availability_bad:ratio5m"),
                    "recording rule execution",
                )
                report.update(
                    {
                        "healthy_scrape_targets": 2,
                        "observed_gateway_requests": float(counts[0]["value"][1]),
                        "observed_gateway_failures": float(errors[0]["value"][1]),
                        "recording_rules_executed": True,
                    }
                )
                if grafana:
                    password = secrets.token_urlsafe(36)
                    environment = {**os.environ, "GF_SECURITY_ADMIN_PASSWORD": password}
                    image = json.loads(
                        (ROOT / "tools.lock.json").read_text(encoding="utf-8")
                    )["images"]["grafana"]
                    subprocess.run(
                        [
                            "docker",
                            "run",
                            "--detach",
                            "--name",
                            container,
                            "--network",
                            "host",
                            "--read-only",
                            "--cap-drop",
                            "ALL",
                            "--security-opt",
                            "no-new-privileges:true",
                            "--tmpfs",
                            "/var/lib/grafana:rw,nosuid,size=128m",
                            "--tmpfs",
                            "/tmp:rw,noexec,nosuid,size=32m",
                            "--mount",
                            f"type=bind,src={ROOT / 'ops/grafana/provisioning'},dst=/etc/grafana/provisioning,readonly",
                            "--mount",
                            f"type=bind,src={ROOT / 'ops/grafana/dashboard.json'},dst=/var/lib/grafana/dashboards/workbench.json,readonly",
                            "--env",
                            "GF_SECURITY_ADMIN_PASSWORD",
                            "--env",
                            "GF_SERVER_HTTP_ADDR=127.0.0.1",
                            "--env",
                            "GF_SERVER_HTTP_PORT=3000",
                            "--env",
                            "GF_AUTH_ANONYMOUS_ENABLED=false",
                            "--env",
                            "GF_USERS_ALLOW_SIGN_UP=false",
                            "--env",
                            "GF_ANALYTICS_REPORTING_ENABLED=false",
                            "--env",
                            "GF_ANALYTICS_CHECK_FOR_UPDATES=false",
                            "--env",
                            "GF_ANALYTICS_CHECK_FOR_PLUGIN_UPDATES=false",
                            "--env",
                            "GF_PLUGINS_PREINSTALL_DISABLED=true",
                            image,
                        ],
                        env=environment,
                        check=True,
                        stdout=subprocess.DEVNULL,
                        timeout=120,
                    )
                    started_container = True
                    authorization = (
                        "Basic "
                        + base64.b64encode(f"admin:{password}".encode()).decode()
                    )
                    dashboard = wait_for(
                        lambda: read_api(
                            3000, "/api/dashboards/uid/sre-workbench", authorization
                        ),
                        "Grafana provisioning",
                    )
                    if (
                        len(dashboard["dashboard"]["panels"]) != 7
                        or "Jason Stys" not in dashboard["dashboard"]["title"]
                    ):
                        raise ValueError(
                            "provisioned dashboard differs from reviewed source"
                        )
                    health = read_api(
                        3000,
                        "/api/datasources/uid/workbench-prometheus/health",
                        authorization,
                    )
                    if health["status"] != "OK":
                        raise ValueError("Grafana datasource is not functional")
                    data = read_api(
                        3000,
                        "/api/datasources/proxy/uid/workbench-prometheus/api/v1/query?"
                        + urllib.parse.urlencode(
                            {
                                "query": 'sum(workbench_requests_total{service="gateway"})'
                            }
                        ),
                        authorization,
                    )
                    if float(data["data"]["result"][0]["value"][1]) != 40:
                        raise ValueError(
                            "Grafana datasource query differs from actual measured requests"
                        )
                    report.update(
                        {
                            "grafana_version": "13.2.4",
                            "grafana_panels_provisioned": 7,
                            "grafana_datasource_query_requests": 40,
                            "grafana_authentication_enabled": True,
                        }
                    )
                # Prove scrape-loss detection instead of assuming an absent service is healthy.
                lab.servers[0].shutdown()
                lab.servers[0].server_close()
                wait_for(
                    lambda: query('up{job="workbench"} == 0'), "worker scrape loss"
                )
                wait_for(
                    lambda: query(
                        'ALERTS{alertname="TelemetryMissing",alertstate="firing"}'
                    ),
                    "missing telemetry alert",
                )
                report["missing_worker_alert_fired"] = True
            finally:
                if started_container:
                    subprocess.run(
                        ["docker", "rm", "--force", container],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        timeout=30,
                    )
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
    (output / "validation.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    """Run the native stack; --grafana is explicit and never touches this PC's Docker Desktop."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "out/stack")
    parser.add_argument("--grafana", action="store_true")
    arguments = parser.parse_args()
    print(json.dumps(validate(arguments.output, arguments.grafana), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

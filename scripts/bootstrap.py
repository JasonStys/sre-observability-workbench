"""Install hash-verified official native tools; extract only one fixed regular binary. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 45
# variable: MAX_DOWNLOAD — line 46
# definition: install — line 49
# parameter: name — line 49
# variable: repositories — line 51
# variable: platform — line 60
# variable: key — line 73
# variable: lock — line 74
# variable: prefix — line 77
# variable: binary — line 82
# variable: member_name — line 83
# variable: output — line 88
# variable: digest — line 90
# variable: total — line 91
# variable: temporary — line 92
# variable: archive_path — line 93
# variable: response — line 95
# variable: stream — line 96
# variable: data — line 98
# variable: total — line 99
# variable: archive — line 106
# variable: member — line 107
# variable: source — line 110
# variable: target — line 113
# definition: main — line 120
# variable: parser — line 122
# variable: arguments — line 126
# END CODE MAP

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_DOWNLOAD = 512 * 1024 * 1024


def install(name: str) -> Path:
    """Allowlist a tool/platform, stream a capped official archive, verify SHA-256, then copy its binary."""
    repositories = {
        "gitleaks": "gitleaks/gitleaks",
        "trivy": "aquasecurity/trivy",
        "actionlint": "rhysd/actionlint",
        "prometheus": "prometheus/prometheus",
        "promtool": "prometheus/prometheus",
    }
    if name not in repositories:
        raise ValueError("unknown tool")
    platform = (
        "windows"
        if sys.platform == "win32"
        else "linux"
        if sys.platform == "linux"
        else "unsupported"
    )
    if (
        platform == "unsupported"
        or platform == "windows"
        and name not in {"prometheus", "promtool"}
    ):
        raise ValueError("tool/platform not supported by this bootstrap")
    key = f"prometheus-{platform}" if name in {"prometheus", "promtool"} else name
    lock = json.loads((ROOT / "tools.lock.json").read_text(encoding="utf-8"))["tools"][
        key
    ]
    prefix = (
        f"https://github.com/{repositories[name]}/releases/download/v{lock['version']}/"
    )
    if not lock["url"].startswith(prefix):
        raise ValueError("tool source must be the official repository")
    binary = name + (".exe" if platform == "windows" else "")
    member_name = (
        f"prometheus-{lock['version']}.{platform}-amd64/{binary}"
        if key.startswith("prometheus-")
        else name
    )
    output = ROOT / ".tools"
    output.mkdir(exist_ok=True, mode=0o700)
    digest = hashlib.sha256()
    total = 0
    with tempfile.TemporaryDirectory(dir=output) as temporary:
        archive_path = Path(temporary) / "tool.tar.gz"
        with (
            urllib.request.urlopen(lock["url"], timeout=60) as response,
            archive_path.open("wb") as stream,
        ):
            while data := response.read(1024 * 1024):
                total += len(data)
                if total > MAX_DOWNLOAD:
                    raise ValueError("tool download exceeds cap")
                digest.update(data)
                stream.write(data)
        if digest.hexdigest() != lock["sha256"]:
            raise ValueError("checksum mismatch; tool will not be executed")
        with tarfile.open(archive_path, "r:gz") as archive:
            member = archive.getmember(member_name)
            if not member.isfile() or member.size > MAX_DOWNLOAD:
                raise ValueError("tool must be a bounded regular binary")
            source = archive.extractfile(member)
            if source is None:
                raise ValueError("tool binary is missing")
            with source, (Path(temporary) / binary).open("wb") as target:
                shutil.copyfileobj(source, target)
            os.chmod(Path(temporary) / binary, 0o700)
            os.replace(Path(temporary) / binary, output / binary)
    return output / binary


def main() -> int:
    """Fetch only an explicitly selected reviewed tool, not arbitrary URLs or executable archive paths."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "name", choices=["prometheus", "promtool", "gitleaks", "trivy", "actionlint"]
    )
    arguments = parser.parse_args()
    print(install(arguments.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Maintain exhaustive tracked-file README summaries without reading ignored drill outputs. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 32
# variable: BEGIN — line 33
# variable: END — line 33
# variable: SPECIAL — line 34
# definition: description — line 56
# parameter: path — line 56
# variable: content — line 66
# variable: line — line 74
# definition: main — line 82
# variable: parser — line 84
# variable: args — line 86
# variable: files — line 87
# variable: rows — line 95
# variable: path — line 96
# variable: label — line 97
# variable: destination — line 99
# variable: original — line 100
# variable: first — line 101
# variable: last — line 101
# variable: expected — line 102
# END CODE MAP

from __future__ import annotations

import argparse
import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEGIN, END = "<!-- BEGIN FILE GUIDE -->", "<!-- END FILE GUIDE -->"
SPECIAL = {
    ".gitattributes": "Portable LF handling for authored text.",
    ".gitignore": "Excludes local evidence, accounts, binaries, caches and generated build output.",
    "LICENSE": "MIT license for authored source, not third-party vendor code.",
    "pyproject.toml": "Strict Python lint, type, test and coverage configuration.",
    "package.json": "Pinned Node client dependencies, build and testing commands.",
    "package-lock.json": "Complete npm package graph and integrity hashes.",
    "tsconfig.json": "Strict TypeScript compiler and explicit Node type configuration.",
    "requirements.in": "Exact reviewed direct runtime dependencies.",
    "requirements.lock": "Hash-locked portable runtime dependency graph.",
    "requirements-dev.in": "Direct validation dependencies plus the runtime graph.",
    "requirements-dev.lock": "Hash-locked portable validation dependency graph.",
    "tools.lock.json": "Official native tool SHA-256 checksums and pinned Grafana image digest.",
    "ops/grafana/dashboard.json": "Seven read-only SRE panels with attribution, missing-data caveats and fixed PromQL.",
    "docs/reports/drill.json": "Actual synthetic Windows fault/recovery measurement and correlated evidence counts.",
    "docs/reports/drill.html": "Escaped network-inert rendering of the measured synthetic drill.",
    "docs/reports/benchmark.json": "Measured in-memory analyzer timing and allocation evidence.",
    "docs/reports/stack.json": "Actual Windows native Prometheus scrape/rule/missing-worker measurements.",
    "docs/reports/ci.json": "Verified source SHA and final measured GitHub Actions check snapshot.",
}


def description(path: str) -> str:
    """Require a meaningful description for every tracked file; unknown formats fail maintenance checks."""
    if path in SPECIAL:
        return SPECIAL[path]
    if path.startswith("examples/"):
        return (
            "Fictional "
            + Path(path).stem
            + " plan/scenario; not cloud state, credentials or current AWS pricing."
        )
    content = (ROOT / path).read_text(encoding="utf-8")
    if path.endswith(".py"):
        return (ast.get_docstring(ast.parse(content)) or "").splitlines()[0]
    if path.endswith(".md"):
        return content.splitlines()[0].lstrip("# ") + "."
    if path.endswith((".sh", ".yml", ".sql")):
        return next(
            line.lstrip("#- ")
            for line in content.splitlines()
            if line.startswith(("# ", "-- "))
        )
    if path.endswith((".ts", ".mjs")):
        return content.splitlines()[0].strip("/ *")
    raise ValueError(f"missing tracked-file purpose: {path}")


def main() -> int:
    """Generate/check the README inventory using intended Git-tracked files only; stage before generating."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    files = (
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .rstrip("\0")
        .split("\0")
    )
    if files == [""]:
        raise ValueError("stage intended files first")
    rows = ["| File | Purpose |", "| --- | --- |"]
    for path in sorted(files):
        label = path.replace("_", "\\_")
        rows.append(f"| [{label}]({path}) | {description(path).replace('|', '/')} |")
    destination = ROOT / "README.md"
    original = destination.read_text(encoding="utf-8")
    first, last = original.index(BEGIN) + len(BEGIN), original.index(END)
    expected = original[:first] + "\n\n" + "\n".join(rows) + "\n\n" + original[last:]
    if args.check and expected != original:
        raise ValueError("README inventory stale")
    if not args.check:
        destination.write_text(expected, encoding="utf-8", newline="\n")
    print(f"README inventory current: {len(files)} tracked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env bash
# Cross-platform quality, real integration and metadata gates. Created by Jason Stys.
# Functions are delegated to audited Python/TypeScript modules; no downloads, secrets or shell eval here.
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# END CODE MAP
set -euo pipefail
python -m ruff check .
python -m ruff format --check .
python -m mypy
npm test
python -m pytest --cov --cov-report=term-missing
python scripts/code_map.py --check
npm run maps:check
python scripts/file_guide.py --check
python scripts/validate_repo.py
python scripts/benchmark.py

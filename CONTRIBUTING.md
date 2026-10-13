# Contribution and coding conventions

Use Python for instrumentation/evidence reasoning, TypeScript for typed async client I/O, SQL for parameterized storage and Bash for portable orchestration. Avoid adding languages or dependencies merely for a language count. Keep names self-documenting, units explicit, functions cohesive and security/edge-case reasoning visible in contracts.

Add regression tests for every behavior change. Run full validation, native Prometheus cases and actual stack tests where supported. Preserve no-data/failed-attempt distinctions. Do not weaken assertions/coverage/advisory gates to obtain green CI. Do not run faults against a target outside this owned synthetic lab.

Formatting order: `python -m ruff check --fix .`, `python -m ruff format .`, `python scripts/code_map.py`, `npm run maps`, stage intended files, `python scripts/file_guide.py`, then run check modes. Generated header maps use AST line locations (Python/TypeScript); declared YAML/SQL/shell tokens use a non-executing lexical map. Descriptive functions/classes and explanatory comments complement the exact map. Lock files and machine JSON use their natural format and are described in the file guide.

Review exact dependencies, official hashes, security advisories and action permissions when updating pins. Keep raw output, databases, downloaded binaries, credentials, generated Node builds and caches outside Git. Publish only deliberately selected synthetic aggregate reports with reproduction commands, source SHA/CI links and honest measurement limitations. Respect MIT and separate vendor licenses.

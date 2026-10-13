"""Exact source-map idempotence and function-line regression tests. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_python_map_positions — line 23
# variable: source — line 25
# variable: result — line 26
# variable: node — line 28
# definition: test_sql_and_shell_map — line 37
# variable: source — line 39
# variable: result — line 40
# variable: line — line 43
# variable: content — line 45
# variable: index — line 45
# variable: sql — line 49
# END CODE MAP

from __future__ import annotations

import ast

from scripts.code_map import mapped, shell_mapped


def test_python_map_positions() -> None:
    """A generated Python function/parameter/variable map must agree with the final parsed source."""
    source = '"""Fictional test module."""\nfrom __future__ import annotations\nx = 1\ndef work(value: int) -> int:\n    """Return a bounded fictional value."""\n    result = value + x\n    return result\n'
    result = mapped(source)
    assert mapped(result) == result
    for node in ast.walk(ast.parse(result)):
        if isinstance(node, ast.FunctionDef):
            assert f"# definition: {node.name} — line {node.lineno}" in result
        elif isinstance(node, ast.arg):
            assert f"# parameter: {node.arg} — line {node.lineno}" in result
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            assert f"# variable: {node.id} — line {node.lineno}" in result


def test_sql_and_shell_map() -> None:
    """Lexical declaration maps preserve shebangs/comments and remain stable under repeated maintenance."""
    source = '#!/usr/bin/env bash\n# Fictional script.\nitem=1\necho "$item"\n'
    result = shell_mapped(source, ".sh")
    assert result.startswith("#!/usr/bin/env bash\n")
    assert shell_mapped(result, ".sh") == result
    line = next(
        index
        for index, content in enumerate(result.splitlines(), 1)
        if content == "item=1"
    )
    assert f"variable: item — line {line}" in result
    sql = shell_mapped(
        "-- Fictional schema.\nCREATE TABLE demo (value INTEGER);\n", ".sql"
    )
    assert "column: value" in sql and "table: demo" in sql
    assert shell_mapped(sql, ".sql") == sql

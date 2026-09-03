"""Run the backend tests and produce a dependency-free line coverage report."""

from __future__ import annotations

import dis
import json
import threading
import trace
from datetime import datetime, timezone
from pathlib import Path
from types import CodeType

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[2]
APP_DIR = BACKEND_DIR / "app"
REPORT_PATH = APP_DIR / "evaluation" / "reports" / "coverage_summary.json"


def _code_lines(code: CodeType) -> set[int]:
    lines = {line for _offset, line in dis.findlinestarts(code)}
    for value in code.co_consts:
        if isinstance(value, CodeType):
            lines.update(_code_lines(value))
    return lines


def _source_lines(path: Path) -> set[int]:
    code = compile(path.read_text(encoding="utf-8"), str(path), "exec")
    return _code_lines(code)


def run() -> tuple[int, dict]:
    # Filter to project files after tracing; omitting ignoredirs keeps API calls
    # executed in TestClient worker threads visible to the standard tracer.
    tracer = trace.Trace(count=True, trace=False)
    previous_thread_trace = threading.gettrace()
    threading.settrace(tracer.globaltrace)
    try:
        exit_code = tracer.runfunc(pytest.main, ["-q", "app/tests"])
    finally:
        threading.settrace(previous_thread_trace)

    executed_by_file: dict[Path, set[int]] = {}
    for (filename, line_number), count in tracer.results().counts.items():
        if count <= 0:
            continue
        path = Path(filename).resolve()
        try:
            path.relative_to(APP_DIR)
        except ValueError:
            continue
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue
        executed_by_file.setdefault(path, set()).add(line_number)

    files = []
    total_lines = 0
    covered_lines = 0
    for path in sorted(APP_DIR.rglob("*.py")):
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue
        executable = _source_lines(path)
        covered = executable & executed_by_file.get(path.resolve(), set())
        total_lines += len(executable)
        covered_lines += len(covered)
        files.append({
            "file": path.relative_to(BACKEND_DIR).as_posix(),
            "executable_lines": len(executable),
            "covered_lines": len(covered),
            "coverage": round(len(covered) / len(executable) * 100, 2) if executable else 100.0,
        })

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": "python -m app.evaluation.run_coverage",
        "test_exit_code": int(exit_code),
        "executable_lines": total_lines,
        "covered_lines": covered_lines,
        "coverage": round(covered_lines / total_lines * 100, 2) if total_lines else 0,
        "files": files,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return int(exit_code), summary


def main() -> None:
    exit_code, summary = run()
    print(json.dumps({key: value for key, value in summary.items() if key != "files"}, ensure_ascii=False, indent=2))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()

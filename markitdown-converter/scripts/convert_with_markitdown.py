#!/usr/bin/env python3
"""Run Microsoft MarkItDown with Windows-friendly path handling, without requiring a project venv."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def can_run_python_module(python_exe: str) -> bool:
    probe = subprocess.run(
        [python_exe, "-c", "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('markitdown') else 1)"],
        text=True,
        capture_output=True,
    )
    return probe.returncode == 0


def find_markitdown_cmd(workspace: Path | None, python_exe: str | None) -> list[str]:
    from_path = shutil.which("markitdown")
    if from_path:
        return [from_path]

    candidates: list[str] = []
    if python_exe:
        candidates.append(python_exe)
    candidates.append(sys.executable)
    py_from_path = shutil.which("python")
    if py_from_path:
        candidates.append(py_from_path)

    seen: set[str] = set()
    for candidate in candidates:
        normalized = str(Path(candidate).resolve()) if Path(candidate).exists() else candidate
        if normalized in seen:
            continue
        seen.add(normalized)
        if can_run_python_module(candidate):
            return [candidate, "-m", "markitdown"]

    legacy_candidates: list[Path] = []
    if workspace is not None:
        legacy_candidates.append(workspace / ".venv" / "Scripts" / "markitdown.exe")
    legacy_candidates.append(Path.cwd() / ".venv" / "Scripts" / "markitdown.exe")
    for candidate in legacy_candidates:
        if candidate.exists():
            return [str(candidate)]

    raise SystemExit(
        "Could not find MarkItDown. Install without a project venv, for example: "
        "python -m pip install --user 'markitdown[all]'"
    )


def default_output(input_path: Path, workspace: Path | None) -> Path:
    base = input_path.with_suffix(".md").name
    if workspace is not None:
        return workspace / base
    return input_path.with_suffix(".md")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert a local file to Markdown with MarkItDown.")
    parser.add_argument("input", help="Input file path, e.g. C:\\Users\\Me\\Desktop\\file.docx")
    parser.add_argument("--output", "-o", help="Output Markdown path. Defaults to <input-name>.md in workspace or beside input.")
    parser.add_argument("--workspace", help="Writable workspace for default output. Defaults to current directory.")
    parser.add_argument("--python", help="Python executable to try for `python -m markitdown`.")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file does not exist: {input_path}")

    workspace = Path(args.workspace).expanduser().resolve() if args.workspace else Path.cwd().resolve()
    output_path = Path(args.output).expanduser().resolve() if args.output else default_output(input_path, workspace)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = find_markitdown_cmd(workspace, args.python) + [str(input_path), "-o", str(output_path)]
    completed = subprocess.run(cmd, text=True, capture_output=True)

    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)

    if completed.returncode != 0:
        return completed.returncode

    if not output_path.exists() or output_path.stat().st_size == 0:
        print(f"Conversion finished but output is missing or empty: {output_path}", file=sys.stderr)
        return 2

    print(f"Markdown written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

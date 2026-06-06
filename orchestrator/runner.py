"""Run Person B and Person C black-box scripts."""

import re
import shlex
import subprocess
import sys
from pathlib import Path


class OrchestratorError(Exception):
    """Friendly pipeline failure."""


def run_generate(intake_path: str, dry_run: bool) -> str:
    command = [sys.executable, "generate.py", "--intake", intake_path]
    if dry_run:
        print(f"[DRY RUN] {shlex.join(command)}")
        return "content.json"

    result = _run(command, "generate.py")
    content_path = _json_path_from_stdout(result.stdout) or "content.json"
    if not Path(content_path).exists():
        raise OrchestratorError(
            f"generate.py completed but expected content file was not found: {content_path}"
        )
    return content_path


def run_render(intake_path: str, content_path: str, dry_run: bool) -> None:
    command = [
        sys.executable,
        "render.py",
        "--intake",
        intake_path,
        "--content",
        content_path,
    ]
    if dry_run:
        print(f"[DRY RUN] {shlex.join(command)}")
        return

    _run(command, "render.py")
    expected = ["output.pptx", "prebite.docx", "postbite.docx"]
    missing = [path for path in expected if not Path(path).exists()]
    if missing:
        raise OrchestratorError(
            f"render.py completed but expected output files were not found: {', '.join(missing)}"
        )


def _run(command: list[str], name: str) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as exc:
        raise OrchestratorError(f"Could not start {name}: {exc}") from exc
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "No error details provided."
        raise OrchestratorError(f"{name} failed: {detail}")
    if result.stdout.strip():
        print(result.stdout.strip())
    return result


def _json_path_from_stdout(stdout: str) -> str | None:
    matches = re.findall(r"(?<![\w./-])([\w./-]+\.json)(?![\w./-])", stdout)
    return matches[-1] if matches else None

"""Run Person B and Person C black-box scripts."""

import re
import shlex
import subprocess
import sys
from pathlib import Path


class OrchestratorError(Exception):
    """Friendly pipeline failure."""


def run_generate(intake_path: str, dry_run: bool) -> str:
    intake = Path(intake_path)
    output_dir = intake.parent / "output"
    expected_path = output_dir / "slides_L1.json"
    command = [
        sys.executable,
        "generate.py",
        "--intake",
        str(intake),
        "--output-dir",
        str(output_dir),
    ]
    if dry_run:
        print(f"[DRY RUN] {shlex.join(command)}")
        return str(expected_path)

    result = _run(command, "generate.py")
    stdout_path = _json_path_from_stdout(result.stdout)
    content_path = Path(stdout_path) if stdout_path and Path(stdout_path).exists() else expected_path
    if not content_path.exists():
        raise OrchestratorError(
            f"generate.py completed but expected content file was not found: {content_path}"
        )
    return str(content_path)


def run_render(intake_path: str, content_path: str, dry_run: bool) -> None:
    output_dir = Path(content_path).parent
    command = [
        sys.executable,
        "render.py",
        "--intake",
        intake_path,
        "--content",
        content_path,
        "--output-dir",
        str(output_dir),
    ]
    if dry_run:
        print(f"[DRY RUN] {shlex.join(command)}")
        return

    _run(command, "render.py")
    expected_groups = {
        "PowerPoint": [output_dir / "output.pptx", *output_dir.glob("training_L*.pptx")],
        "pre-bite": [output_dir / "prebite.docx", *output_dir.glob("prebite_L*.docx")],
        "post-bite": [output_dir / "postbite.docx", *output_dir.glob("postbite_L*.docx")],
    }
    missing = [name for name, candidates in expected_groups.items() if not any(path.exists() for path in candidates)]
    if missing:
        raise OrchestratorError(
            f"render.py completed but expected output categories were not found in {output_dir}: {', '.join(missing)}"
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

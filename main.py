"""Maverx Person A CLI: intake, validation gate, and orchestration."""

import argparse
import json
import time
import traceback
from pathlib import Path

from intake.parser import derive_slide_target
from intake.questions import IntakeAborted, collect_intake
from intake.validator import (
    DIDACTIC_BLOCKS,
    SPEAKER_NOTES_FIELDS,
    score_intake,
    validate_intake,
)
from orchestrator.runner import OrchestratorError, run_generate, run_render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a validated Maverx training intake.")
    parser.add_argument("--dry-run", action="store_true", help="Print downstream commands without running them.")
    parser.add_argument("--resume", action="store_true", help="Resume valid answers from intake_draft.json.")
    parser.add_argument("--output", default="./intake.json", help="Intake JSON output path.")
    parser.add_argument("--debug", action="store_true", help="Show tracebacks for errors.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    started = time.monotonic()
    try:
        data = collect_intake(resume=args.resume)
        data.update(
            {
                "slide_target": derive_slide_target(data["duration_hours"], data["tier"]),
                "didactic_blocks": DIDACTIC_BLOCKS,
                "speaker_notes_fields": SPEAKER_NOTES_FIELDS,
                "prebite_required": True,
                "postbite_required": True,
                "cost_tracking_required": True,
                "slide_confidence_required": True,
                "iterative_confirmation_required": True,
            }
        )

        issues = validate_intake(data)
        score, breakdown = score_intake(data)
        if issues:
            print("[INTAKE ERROR]")
            for issue in issues:
                print(issue)
        print_score(score, breakdown)
        if issues or score < 80:
            print("Generation refused until the intake passes validation and scores at least 80.")
            return 1

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"[INTAKE] Saved validated intake: {output_path.resolve()}")

        content_path = run_generate(str(output_path), args.dry_run)
        run_render(str(output_path), content_path, args.dry_run)
        return 0
    except (IntakeAborted, OrchestratorError, OSError, ValueError) as exc:
        if args.debug:
            traceback.print_exc()
        else:
            print(f"[ERROR] {exc}")
        return 1
    except Exception:
        if args.debug:
            traceback.print_exc()
        else:
            print("[ERROR] Unexpected failure. Re-run with --debug for details.")
        return 1
    finally:
        print(f"[RUNTIME] {time.monotonic() - started:.2f} seconds")


def print_score(score: int, breakdown: dict) -> None:
    suffix = "" if score >= 80 else " - minimum 80 required."
    print(f"[SCORE] Training Readiness: {score}/100{suffix}")
    for key, result in breakdown.items():
        marker = "✓" if result["score"] == result["max"] else "✗"
        print(f"{key:<18} {marker} {result['score']}/{result['max']}")


if __name__ == "__main__":
    raise SystemExit(main())

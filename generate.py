"""Person B deterministic fallback generator."""

import argparse
import json
import os
import tempfile
import traceback
from pathlib import Path

from generation.artifacts import generate_artifacts
from generation.fallback import generate_deck
from generation.validator import ensure_valid, validate_artifacts, validate_deck


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate deterministic Maverx training content.")
    parser.add_argument("--intake", default="./intake.json", help="Path to Person A intake JSON.")
    parser.add_argument("--output-dir", default=".", help="Directory for generated JSON files.")
    parser.add_argument("--debug", action="store_true", help="Show tracebacks for errors.")
    return parser


def generate_all(intake: dict) -> dict[str, dict]:
    levels = [1] if intake.get("tier") == 1 else [1, 2, 3]
    outputs = {}
    for level in levels:
        deck = generate_deck(intake, level)
        prebite, postbite, dataset = generate_artifacts(intake, level)
        ensure_valid(validate_deck(deck, intake, level))
        ensure_valid(validate_artifacts(prebite, postbite, dataset, intake, level))
        outputs[f"slides_L{level}.json"] = deck
        outputs[f"prebite_L{level}.json"] = prebite
        outputs[f"postbite_L{level}.json"] = postbite
        outputs[f"dataset_spec_L{level}.json"] = dataset
    return outputs


def write_outputs(outputs: dict[str, dict], output_dir: str | Path) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for filename, data in outputs.items():
        path = directory / filename
        _atomic_write_json(path, data)
        paths.append(path.resolve())
    return paths


def _atomic_write_json(path: Path, data: dict) -> None:
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def main() -> int:
    args = build_parser().parse_args()
    try:
        intake = json.loads(Path(args.intake).read_text(encoding="utf-8"))
        outputs = generate_all(intake)
        paths = write_outputs(outputs, args.output_dir)
        for path in paths:
            print(f"[GENERATED] {path}")
        primary = next(path for path in paths if path.name == "slides_L1.json")
        print(primary)
        return 0
    except Exception as exc:
        if args.debug:
            traceback.print_exc()
        else:
            print(f"[GENERATION ERROR] {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

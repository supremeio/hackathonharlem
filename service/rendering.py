"""Render generated decks to .pptx via Person C's renderer.

Tier 1 produces a single .pptx; Tier 2/3 bundle the per-level decks into a zip.
Returns the download filename (relative to the deck directory), or None if
rendering is unavailable.
"""

import json
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MASTER = PROJECT_ROOT / "maverx_master.pptx"


def render_decks(intake: dict, deck_dir: Path, levels: list[int]) -> str | None:
    try:
        from render import render_deck
    except Exception as exc:  # python-pptx missing, etc.
        print(f"[RENDER UNAVAILABLE] {exc}")
        return None

    intake_path = deck_dir / "intake.json"
    intake_path.write_text(json.dumps(intake, ensure_ascii=False, indent=2), encoding="utf-8")

    rendered: list[Path] = []
    for level in levels:
        content_path = deck_dir / f"slides_L{level}.json"
        out_path = deck_dir / f"slides_L{level}.pptx"
        try:
            render_deck(str(intake_path), str(content_path), str(MASTER), str(out_path))
            rendered.append(out_path)
        except Exception as exc:
            print(f"[RENDER ERROR] L{level}: {exc}")

    if not rendered:
        return None
    if len(rendered) == 1:
        return rendered[0].name

    zip_path = deck_dir / "slides.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in rendered:
            archive.write(path, path.name)
    return zip_path.name

"""
End-to-end pipeline: validated intake answers -> deck + pre/post-bite on disk.

This is the single integration point both front-ends (Streamlit app, CLI) call.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

from .bites import build_bites
from .config import OUTPUT_DIR
from .deck import build_deck
from .llm import OpenRouterClient
from .planner import plan_training
from .schema import Training


@dataclass
class GenerationResult:
    training: Training
    pptx_path: str
    prebite_path: str
    postbite_path: str
    plan_json_path: str
    slug: str
    generated_by: str


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return (s or "training")[:50]


def generate_training(
    answers: dict,
    out_dir: Optional[Path] = None,
    use_llm: bool = True,
    progress: Optional[Callable[[str], None]] = None,
) -> GenerationResult:
    out_dir = Path(out_dir or OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    def say(msg: str):
        if progress:
            progress(msg)

    llm = OpenRouterClient() if use_llm else None
    if llm is not None and not llm.available:
        say("No OPENROUTER_API_KEY found — using the offline template engine.")
        llm = None

    say("Planning the training structure…")
    tr = plan_training(answers, llm=llm, progress=progress)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = f"{_slugify(tr.title)}_{stamp}"

    say("Building the PowerPoint on the Maverx master…")
    pptx_path = build_deck(tr, out_dir / f"{slug}.pptx")

    say("Writing the pre-bite and post-bite documents…")
    pre, post = build_bites(tr, out_dir, slug)

    plan_path = out_dir / f"{slug}_plan.json"
    plan_path.write_text(json.dumps(tr.to_dict(), indent=2, default=str),
                         encoding="utf-8")

    say("Done.")
    return GenerationResult(
        training=tr,
        pptx_path=pptx_path,
        prebite_path=pre,
        postbite_path=post,
        plan_json_path=str(plan_path),
        slug=slug,
        generated_by=tr.generated_by,
    )

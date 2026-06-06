"""
Maverx house-style specification + runtime configuration.

Everything visual the generator needs lives here, extracted directly from the
Maverx "Presentation Style Guide" deck. To re-skin the agent for a different
brand, swap the master .pptx in ``assets/`` and edit the constants below — no
other file needs to change. (See README → "Swapping the style guide".)
"""

from __future__ import annotations

import os
from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
PKG_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PKG_DIR / "assets"
PROJECT_DIR = PKG_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "output"

# The master template the deck is built ON (referenced, never redrawn).
MASTER_TEMPLATE = ASSETS_DIR / "maverx_master.pptx"
# A branded-but-empty copy (all sample slides stripped, masters/layouts kept),
# produced by tools/make_blank.py. The generator builds on THIS.
BLANK_TEMPLATE = ASSETS_DIR / "maverx_blank.pptx"

OUTPUT_DIR.mkdir(exist_ok=True)


# --------------------------------------------------------------------------- #
# Brand colours  (hex, no leading '#')  — taken from the style guide
# --------------------------------------------------------------------------- #
class Color:
    INDIGO = "0D006A"      # primary — titles & main text
    PURPLE = "5400AD"      # secondary accent / icons
    ORANGE = "F79421"      # highlight / emphasis words
    ORANGE_ALT = "F59235"
    CORAL = "EF4453"       # subtitles / attention
    MAGENTA = "D3116E"     # accent / icons
    GOLD = "BF9000"
    NAVY = "002060"
    BLACK = "3A3838"
    WHITE = "FFFFFF"

    # Light tint backgrounds (max three base colours per slide rule)
    CREAM = "FBF2E2"
    PEACH = "FBE5D6"
    LAVENDER = "F1EDF9"
    PINK_TINT = "F6E5F0"
    CARD_BG = "FFFFFF"
    SLIDE_TINT = "E9ECF2"  # the light grey-blue used on the "About this session" slide

    # Ordered palette for numbered circles / category icons (style-guide order)
    SEQUENCE = [PURPLE, MAGENTA, GOLD, ORANGE, BLACK]


# --------------------------------------------------------------------------- #
# Typography  — sizes in points, lifted from style-guide slide 3
# --------------------------------------------------------------------------- #
class Font:
    TITLE = "Space Grotesk"     # headings
    BODY = "Space Grotesk"      # body / bullets (house style: single typeface)
    BODY_ALT = "Space Grotesk"

    SIZE_TITLE = 40             # slide titles (style guide: 44; trimmed for fit)
    SIZE_COVER_TITLE = 40
    SIZE_SUBTITLE = 28
    SIZE_SUBSUB = 24
    SIZE_MAIN = 22             # main bullet text (22-24 & bold)
    SIZE_SUB = 18              # subtext (18-20, regular)
    SIZE_SMALL = 14
    SIZE_CARD_HEAD = 20
    SIZE_BADGE = 11


# --------------------------------------------------------------------------- #
# Named layouts available in the master (used, not recreated)
# --------------------------------------------------------------------------- #
class Layout:
    COVER = "Startscherm Paars"          # purple branded start screen
    COVER_ALT = "TITLE"
    SECTION = "Beeldmerk Oranje"         # orange brand-mark divider
    CONTENT = "Titeldia"                 # white content slide w/ logo + footer
    CONTENT_GREY = "Foto Slide Grijs"
    GRADIENT_LIGHT = "Foto Slide Gradient Licht"
    GRADIENT_DARK = "Foto Slide Gradient Donker "  # trailing space is in the file
    BLANK = "Aangepaste indeling"


# Role -> (master_index, layout_name).  Calibrated by rendering every layout and
# measuring pixel luminance (tools/calibrate_layouts.py).  This template ships
# 10 masters that reuse layout names, so we pin the master index too.
#   * cover/divider/closing  -> dark branded layouts (white text)
#   * content                -> pure-white layout carrying the logo + footer
# When swapping in a new style guide, re-run tools/calibrate_layouts.py and
# paste the new map here. The generator falls back to first-match-by-name if a
# pinned (master,name) pair is absent, so it degrades gracefully.
LAYOUT_MAP = {
    "cover":   (0, "TITLE"),
    "section": (1, "Foto Slide Gradient Donker "),
    "content": (1, "Titeldia"),
    "tint":    (2, "Titeldia"),
    "closing": (1, "Foto Slide Gradient Donker "),
    "break":   (1, "Foto Slide Gradient Licht"),
}

# Slide geometry (inches) for the 13.333 x 7.5 widescreen master.
class Geo:
    SLIDE_W = 13.333
    SLIDE_H = 7.5
    MARGIN_L = 0.85
    MARGIN_R = 0.7
    TITLE_TOP = 0.35
    TITLE_H = 1.05
    BODY_TOP = 1.65
    BODY_BOTTOM = 6.95     # keep clear of the footer furniture

    @classmethod
    def content_w(cls):
        return cls.SLIDE_W - cls.MARGIN_L - cls.MARGIN_R


# --------------------------------------------------------------------------- #
# The fixed Maverx didactic model — enforced, no exceptions
# (brief: Kick-off → Theory → Example → Exercise → Wrap-up,
#  style guide: Before / Per-topic / After framing)
# --------------------------------------------------------------------------- #
DIDACTIC_BLOCKS = ["Kick-off", "Theory", "Example", "Exercise", "Wrap-up"]

# The 6 speaker-note fields (brief requires 5; the style guide expects these 6,
# which is a strict superset, so we satisfy both).
SPEAKER_NOTE_FIELDS = [
    "Aim",
    "Time",
    "Instructions",
    "Key discussion points",
    "Link to reality",
    "Reflective question",
    "Debrief & summary",
]

# The 5 mandatory intake questions (verbatim intent from the brief).
INTAKE_QUESTIONS = [
    {
        "key": "topic",
        "question": "What is the topic or skill to be trained?",
        "why": "Sets the domain.",
    },
    {
        "key": "audience",
        "question": "Who is the target audience?",
        "why": "Sets tone and depth.",
    },
    {
        "key": "level",
        "question": "What is the knowledge level of participants? "
                    "(beginner / intermediate / advanced)",
        "why": "Calibrates difficulty.",
    },
    {
        "key": "duration",
        "question": "How long is the training? (e.g. 2 hours, half a day)",
        "why": "Determines module count and slide count.",
    },
    {
        "key": "objective",
        "question": "What is the primary learning objective? "
                    "(what should participants be able to DO afterwards?)",
        "why": "Anchors the entire structure.",
    },
]


# --------------------------------------------------------------------------- #
# LLM configuration (OpenRouter)
# --------------------------------------------------------------------------- #
class LLM:
    BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    # Sensible default; override with OPENROUTER_MODEL. Any OpenRouter model works.
    MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4.6")
    TEMPERATURE = float(os.getenv("OPENROUTER_TEMPERATURE", "0.5"))
    MAX_TOKENS = int(os.getenv("OPENROUTER_MAX_TOKENS", "8000"))
    # Optional attribution headers OpenRouter recommends.
    APP_NAME = "Maverx Training Builder"
    APP_URL = "https://maverx.nl"

    @classmethod
    def available(cls) -> bool:
        return bool(cls.API_KEY)


def duration_to_minutes(text: str) -> int:
    """Best-effort parse of a free-text duration into minutes."""
    import re

    t = text.lower().strip()
    if not t:
        return 120
    if "half" in t and "day" in t:
        return 240
    if "full" in t and "day" in t:
        return 480
    if "day" in t and not any(c.isdigit() for c in t):
        return 480

    nums = re.findall(r"(\d+(?:[.,]\d+)?)", t)
    if not nums:
        return 120
    val = float(nums[0].replace(",", "."))
    if "day" in t:
        return int(val * 480)
    if "min" in t:
        return int(val)
    # default unit = hours
    return int(val * 60)

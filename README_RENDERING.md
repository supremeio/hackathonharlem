# Person C — Rendering

This document covers the rendering layer that converts Person B's structured JSON into a fully editable Maverx-style PowerPoint deck plus Markdown side-documents.

## What renders

- output.pptx — the full training deck, ~20 slides for Tier 1
- prebite.md — participant preparation document
- postbite.md — participant follow-up document

All three files open and edit cleanly: titles, bullets, and speaker notes are text fields, not flattened images.

## Quickstart

After Person A and B have run, install dependencies and render:

    pip install python-pptx
    python render.py --intake intake.json --content output/slides_L1.json --prebite output/prebite_L1.json --postbite output/postbite_L1.json --output output.pptx

## How layouts are chosen

maverx_master.pptx provides 8 layouts that reflect the Maverx house style (cover, section, agenda, title+bullets, two-column, 3-card grid, 4-quadrant, closing). Each slide_type from the content JSON is mapped to the layout that best fits its didactic role.

- kickoff_title → Cover (title + subtitle on dark purple background)
- kickoff_agenda → Agenda (photo + section list)
- kickoff_objectives → 4-Quadrant (objectives spread visually)
- theory_intro → Title + bullets (first concept introduction)
- theory_deep → 3-Card grid (concept broken into 3 ideas)
- example_walkthrough → Two-column (scenario + step-by-step)
- example_case → 3-Card grid (case split across cards)
- exercise_setup → Title + bullets (exercise framing)
- exercise_instructions → 3-Card grid (numbered steps as cards)
- wrapup_summary → Closing (takeaways)
- wrapup_nextlevel → Closing (what's next)

## Speaker notes

Each slide receives a 6-field facilitation guide written into the PowerPoint notes pane:

- AIM — purpose of the slide
- TIME — facilitation estimate
- INSTRUCTIONS — what the trainer says and does
- KEY DISCUSSION POINTS — what must land
- LINK TO REALITY — concrete analogy
- REFLECTIVE QUESTION — to ask the room
- DEBRIEF — punchy closing line

This matches the Maverx style guide expectations for the facilitation guide.

## House style compliance

The renderer never draws shapes, colors, or backgrounds itself. All visual styling — the Maverx logo, footer, color palette, typography, decorative accents — lives in maverx_master.pptx. The renderer fills placeholders only. This guarantees consistency with the brand and makes the master swappable for future style updates.

## Side documents

prebite.md and postbite.md are generated as clean Markdown rather than .docx to keep the renderer dependency-light and the output universally editable. They open in any text editor, Notion, Obsidian, or convert trivially to Word via Pandoc.

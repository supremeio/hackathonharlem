import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generate import generate_all, write_outputs
from generation.artifacts import generate_artifacts
from generation.fallback import ALLOCATIONS, BLOCK_ORDER, generate_deck
from generation.validator import (
    NOTE_FIELDS,
    load_allowed_slide_types,
    validate_artifacts,
    validate_deck,
)


def sample_intake(language="en", tier=2):
    return {
        "tier": tier,
        "topic": "Power BI dashboard design",
        "audience": "marketing analysts reporting campaign performance",
        "knowledge_level": "beginner",
        "duration_hours": 3.0,
        "primary_objective": "Build and explain a campaign performance dashboard.",
        "outline_path": "trainer_supplied",
        "output_language": language,
        "level": 1,
        "presupposes": ["data import", "basic charts", "filters"],
        "slide_target": 36,
        "didactic_blocks": BLOCK_ORDER,
        "speaker_notes_fields": ["aim", "time", "instructions", "reflective_question", "debrief"],
        "prebite_required": True,
        "postbite_required": True,
        "cost_tracking_required": True,
        "slide_confidence_required": True,
        "iterative_confirmation_required": True,
    }


class DeckGenerationTests(unittest.TestCase):
    def test_each_level_has_exactly_20_slides_and_allocation(self):
        for level in (1, 2, 3):
            with self.subTest(level=level):
                deck = generate_deck(sample_intake(), level)
                self.assertEqual(len(deck["slides"]), 20)
                counts = {block: 0 for block in BLOCK_ORDER}
                for slide in deck["slides"]:
                    counts[slide["block"]] += 1
                self.assertEqual(counts, ALLOCATIONS[level])

    def test_exact_contiguous_block_order_and_sequential_numbers(self):
        deck = generate_deck(sample_intake(), 2)
        condensed = []
        for slide in deck["slides"]:
            if not condensed or condensed[-1] != slide["block"]:
                condensed.append(slide["block"])
        self.assertEqual(condensed, BLOCK_ORDER)
        self.assertEqual([slide["slide_number"] for slide in deck["slides"]], list(range(1, 21)))

    def test_only_existing_maverx_slide_types_are_used(self):
        allowed = load_allowed_slide_types()
        for level in (1, 2, 3):
            used = {slide["slide_type"] for slide in generate_deck(sample_intake(), level)["slides"]}
            self.assertTrue(used.issubset(allowed))

    def test_required_slide_and_speaker_note_fields(self):
        slide = generate_deck(sample_intake(), 1)["slides"][0]
        required = {
            "slide_number", "slide_type", "block", "level", "title", "body", "table",
            "visual_suggestion", "confidence_score", "confidence_reason", "speaker_notes",
        }
        self.assertTrue(required.issubset(slide))
        self.assertTrue(set(NOTE_FIELDS).issubset(slide["speaker_notes"]))
        self.assertTrue(slide["speaker_notes"]["key_discussion_points"])

    def test_mentimeter_progression(self):
        for level, expected in ((1, 0), (2, 1), (3, 1)):
            deck = generate_deck(sample_intake(), level)
            recaps = [slide for slide in deck["slides"] if slide["slide_type"] == "mentimeter_recap"]
            self.assertEqual(len(recaps), expected)
            if recaps:
                self.assertEqual(len(recaps[0]["body"]), 5)

    def test_level_progression_is_explicit(self):
        level2 = json.dumps(generate_deck(sample_intake(), 2), ensure_ascii=False).lower()
        level3 = json.dumps(generate_deck(sample_intake(), 3), ensure_ascii=False).lower()
        self.assertIn("level 1", level2)
        self.assertIn("level 1", level3)
        self.assertIn("level 2", level3)

    def test_decks_validate(self):
        intake = sample_intake()
        for level in (1, 2, 3):
            self.assertEqual(validate_deck(generate_deck(intake, level), intake, level), [])

    def test_cost_tracking_is_zero_cost_fallback(self):
        cost = generate_deck(sample_intake(), 1)["cost_tracking"]
        self.assertEqual(cost["model_name"], "deterministic-fallback")
        self.assertGreater(cost["input_tokens_estimate"], 0)
        self.assertGreater(cost["output_tokens_estimate"], 0)
        self.assertEqual(cost["estimated_cost_eur"], 0.0)


class LanguageTests(unittest.TestCase):
    def test_english_output(self):
        slide = generate_deck(sample_intake("en"), 1)["slides"][0]
        self.assertNotIn("NL:", slide["title"])

    def test_dutch_output(self):
        slide = generate_deck(sample_intake("nl"), 1)["slides"][0]
        self.assertIn("praktische", slide["body"][0].lower())
        self.assertNotIn("EN:", slide["title"])

    def test_bilingual_output_uses_flat_strings(self):
        slide = generate_deck(sample_intake("bilingual"), 1)["slides"][0]
        self.assertIsInstance(slide["title"], str)
        self.assertIn("NL:", slide["title"])
        self.assertIn("EN:", slide["title"])
        self.assertTrue(all(isinstance(item, str) for item in slide["body"]))


class ArtifactTests(unittest.TestCase):
    def test_all_artifacts_validate_and_complexity_increases(self):
        intake = sample_intake()
        column_counts = []
        for level in (1, 2, 3):
            prebite, postbite, dataset = generate_artifacts(intake, level)
            self.assertEqual(validate_artifacts(prebite, postbite, dataset, intake, level), [])
            column_counts.append(len(dataset["columns"]))
        self.assertEqual(column_counts, sorted(column_counts))
        self.assertEqual(len(set(column_counts)), 3)

    def test_postbites_bridge_to_next_prebites(self):
        intake = sample_intake()
        _, post1, _ = generate_artifacts(intake, 1)
        _, post2, _ = generate_artifacts(intake, 2)
        _, post3, _ = generate_artifacts(intake, 3)
        self.assertIn("Level 2", post1["next_level_bridge"])
        self.assertIn("Level 3", post2["next_level_bridge"])
        self.assertIn("real-world", post3["next_level_bridge"])


class CliContractTests(unittest.TestCase):
    def test_tier_two_generates_all_twelve_files(self):
        outputs = generate_all(sample_intake(tier=2))
        self.assertEqual(len(outputs), 12)
        self.assertIn("slides_L1.json", outputs)
        self.assertIn("dataset_spec_L3.json", outputs)
        with tempfile.TemporaryDirectory() as directory:
            paths = write_outputs(outputs, directory)
            self.assertEqual(len(paths), 12)
            self.assertTrue(all(path.exists() for path in paths))

    def test_tier_one_generates_only_level_one_files(self):
        outputs = generate_all(sample_intake(tier=1))
        self.assertEqual(len(outputs), 4)
        self.assertTrue(all("_L1.json" in name for name in outputs))


if __name__ == "__main__":
    unittest.main()

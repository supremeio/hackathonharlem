import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from intake.parser import (
    coerce_knowledge_level,
    derive_slide_target,
    parse_duration,
    parse_level,
    parse_outline_path,
    parse_output_language,
    parse_tier,
)
from intake.questions import IntakeAborted, collect_intake
from intake.validator import DIDACTIC_BLOCKS, SPEAKER_NOTES_FIELDS, score_intake, validate_intake
from orchestrator.runner import _json_path_from_stdout
import main as app_main


def valid_intake(level=1):
    return {
        "tier": 1,
        "topic": "Excel pivot tables for finance analysts",
        "audience": "finance analysts producing monthly management reports",
        "knowledge_level": "beginner",
        "duration_hours": 3.0,
        "primary_objective": "By the end of this session, participants will be able to build and explain a pivot table.",
        "outline_path": "research_assisted",
        "output_language": "bilingual",
        "level": level,
        "presupposes": [] if level == 1 else ["data import", "basic charts", "filters"],
        "slide_target": 36,
        "didactic_blocks": DIDACTIC_BLOCKS,
        "speaker_notes_fields": SPEAKER_NOTES_FIELDS,
        "prebite_required": True,
        "postbite_required": True,
        "cost_tracking_required": True,
        "slide_confidence_required": True,
        "iterative_confirmation_required": True,
    }


class ParserTests(unittest.TestCase):
    def test_duration_examples(self):
        examples = {
            "2 hours": 2.0,
            "90 minutes": 1.5,
            "1.5h": 1.5,
            "half a day": 4.0,
            "1 day": 8.0,
            "3": 3.0,
        }
        for raw, expected in examples.items():
            with self.subTest(raw=raw):
                self.assertEqual(parse_duration(raw), expected)

    def test_choice_parsers_and_knowledge(self):
        self.assertEqual(parse_tier("2"), 2)
        self.assertEqual(parse_level("3"), 3)
        self.assertEqual(coerce_knowledge_level(" Beginner "), "beginner")
        for parser in (parse_tier, parse_level):
            with self.assertRaises(ValueError):
                parser("4")

    def test_slide_target_caps(self):
        self.assertEqual(derive_slide_target(1, 1), 30)
        self.assertEqual(derive_slide_target(3, 1), 36)
        self.assertEqual(derive_slide_target(10, 2), 50)
        self.assertEqual(derive_slide_target(20, 3), 80)

    def test_outline_path_parsing(self):
        self.assertEqual(parse_outline_path("1"), "trainer_supplied")
        self.assertEqual(parse_outline_path(" 2 "), "research_assisted")
        with self.assertRaises(ValueError):
            parse_outline_path("3")

    def test_output_language_parsing(self):
        self.assertEqual(parse_output_language("1"), "en")
        self.assertEqual(parse_output_language("2"), "nl")
        self.assertEqual(parse_output_language("3"), "bilingual")
        with self.assertRaises(ValueError):
            parse_output_language("English")


class ValidatorTests(unittest.TestCase):
    def test_valid_intake_scores_100(self):
        data = valid_intake()
        self.assertEqual(validate_intake(data), [])
        self.assertEqual(score_intake(data)[0], 100)

    def test_vague_values_and_missing_presupposes_fail(self):
        data = valid_intake(level=2)
        data["topic"] = "Excel"
        data["audience"] = "employees"
        data["presupposes"] = []
        issues = validate_intake(data)
        self.assertTrue(any(issue.startswith("topic:") for issue in issues))
        self.assertTrue(any(issue.startswith("audience:") for issue in issues))
        self.assertTrue(any(issue.startswith("presupposes:") for issue in issues))
        self.assertLess(score_intake(data)[0], 80)

    def test_new_contract_constants_are_required(self):
        data = valid_intake()
        data["cost_tracking_required"] = False
        data["slide_confidence_required"] = False
        data["iterative_confirmation_required"] = False
        issues = validate_intake(data)
        self.assertTrue(any(issue.startswith("cost_tracking_required:") for issue in issues))
        self.assertTrue(any(issue.startswith("slide_confidence_required:") for issue in issues))
        self.assertTrue(any(issue.startswith("iterative_confirmation_required:") for issue in issues))


class QuestionLoopTests(unittest.TestCase):
    def test_three_invalid_attempts_save_draft(self):
        answers = iter(["4", "4", "4"])
        with tempfile.TemporaryDirectory() as directory:
            draft = Path(directory) / "intake_draft.json"
            with patch("intake.questions.DRAFT_PATH", draft):
                with self.assertRaises(IntakeAborted):
                    collect_intake(input_fn=lambda _: next(answers))
            self.assertEqual(json.loads(draft.read_text())["tier"], "4")

    def test_collects_outline_path_and_output_language(self):
        answers = iter(
            [
                "1",
                "Excel pivot tables for finance analysts",
                "finance analysts producing monthly management reports",
                "beginner",
                "3 hours",
                "By the end of this session, participants will be able to build and explain a pivot table.",
                "1",
                "3",
                "1",
            ]
        )
        data = collect_intake(input_fn=lambda _: next(answers))
        self.assertEqual(data["outline_path"], "trainer_supplied")
        self.assertEqual(data["output_language"], "bilingual")


class OrchestratorTests(unittest.TestCase):
    def test_stdout_json_path(self):
        self.assertEqual(_json_path_from_stdout("Wrote build/slides.json successfully"), "build/slides.json")
        self.assertIsNone(_json_path_from_stdout("Done"))


class MainFlowTests(unittest.TestCase):
    def test_main_writes_new_contract_constants_to_intake_json(self):
        collected = valid_intake()
        for key in (
            "slide_target",
            "didactic_blocks",
            "speaker_notes_fields",
            "prebite_required",
            "postbite_required",
            "cost_tracking_required",
            "slide_confidence_required",
            "iterative_confirmation_required",
        ):
            collected.pop(key)

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "intake.json"
            with (
                patch.object(sys, "argv", ["main.py", "--dry-run", "--output", str(output)]),
                patch("main.collect_intake", return_value=collected),
                patch("main.run_generate", return_value="content.json"),
                patch("main.run_render"),
            ):
                self.assertEqual(app_main.main(), 0)

            written = json.loads(output.read_text())
            self.assertEqual(written["slide_target"], 36)
            self.assertIs(written["cost_tracking_required"], True)
            self.assertIs(written["slide_confidence_required"], True)
            self.assertIs(written["iterative_confirmation_required"], True)


if __name__ == "__main__":
    unittest.main()

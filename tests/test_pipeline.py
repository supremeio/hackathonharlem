"""Smoke tests for the offline maverx pipeline — no network or API key required.

Run: python -m unittest discover -s tests
"""

import tempfile
import unittest
from pathlib import Path

from maverx.config import duration_to_minutes
from maverx.pipeline import generate_training

SAMPLE = {
    "topic": "Writing clear pull request descriptions",
    "audience": "software engineers",
    "level": "beginner",
    "duration": "1 hour",
    "objective": "write PRs that reviewers can approve quickly",
}


class OfflinePipelineTest(unittest.TestCase):
    def test_produces_a_complete_training_and_pptx(self):
        result = generate_training(SAMPLE, out_dir=Path(tempfile.mkdtemp()), use_llm=False)
        tr = result.training

        self.assertTrue(tr.title, "training should have a title")
        self.assertTrue(tr.modules, "expected at least one module")
        self.assertTrue(Path(result.pptx_path).is_file(), "a .pptx should be written")
        self.assertFalse(result.used_llm, "offline run must not claim LLM authorship")

        # Every content block must carry the mandatory speaker-note fields.
        for module in tr.modules:
            for block in (module.theory, module.example, module.exercise):
                self.assertTrue(block.notes.aim)
                self.assertTrue(block.notes.time)
                self.assertTrue(block.notes.instructions)


class DurationParsingTest(unittest.TestCase):
    def test_parses_common_phrasings(self):
        self.assertEqual(duration_to_minutes("2 hours"), 120)
        self.assertEqual(duration_to_minutes("90 minutes"), 90)
        self.assertEqual(duration_to_minutes("half a day"), 240)
        self.assertEqual(duration_to_minutes(""), 120)  # safe default


if __name__ == "__main__":
    unittest.main()

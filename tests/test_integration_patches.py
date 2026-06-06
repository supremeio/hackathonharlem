import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generation.fallback import generate_deck
from tests.test_person_b import sample_intake


class SlideSchemaPatchTests(unittest.TestCase):
    def test_schema_accepts_new_required_fields_and_future_extras(self):
        schema = json.loads((ROOT / "schemas" / "slides_schema.json").read_text())
        item = schema["items"]
        notes = item["properties"]["speaker_notes"]
        for field in ("block", "visual_suggestion", "confidence_score", "confidence_reason"):
            self.assertIn(field, item["required"])
            self.assertIn(field, item["properties"])
        for field in ("key_discussion_points", "link_to_reality"):
            self.assertIn(field, notes["required"])
            self.assertIn(field, notes["properties"])
        self.assertNotEqual(item.get("additionalProperties"), False)
        self.assertNotEqual(notes.get("additionalProperties"), False)

    def test_person_b_slide_contains_schema_required_fields(self):
        schema = json.loads((ROOT / "schemas" / "slides_schema.json").read_text())
        slide = generate_deck(sample_intake(), 1)["slides"][0]
        self.assertTrue(set(schema["items"]["required"]).issubset(slide))


class ObsoletePrototypeApiTests(unittest.TestCase):
    @unittest.skip("Obsolete /generate, /status, and /download routes were replaced by the current /decks API.")
    def test_obsolete_prototype_routes(self):
        pass


if __name__ == "__main__":
    unittest.main()

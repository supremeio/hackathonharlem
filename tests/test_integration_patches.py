import json
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generation.fallback import generate_deck
from tests.test_person_b import sample_intake

FASTAPI_AVAILABLE = importlib.util.find_spec("fastapi") is not None
if FASTAPI_AVAILABLE:
    from api import download, generate, status
    from fastapi import HTTPException


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


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI is not installed; run pip install -r requirements.txt")
class PrototypeApiTests(unittest.TestCase):
    def test_generate_rejects_invalid_intake(self):
        with self.assertRaises(HTTPException) as raised:
            generate({"tier": 2})
        self.assertEqual(raised.exception.status_code, 422)

    def test_generate_and_status_use_configured_output_directory(self):
        intake = sample_intake()
        intake["level"] = 1
        intake["presupposes"] = []
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory).resolve()
            with patch("api.OUTPUT_DIR", output_dir):
                response = generate(intake)
                current = status()
            self.assertEqual(response["score"], 100)
            self.assertEqual(response["output_dir"], str(output_dir))
            self.assertEqual(len(response["files"]), 12)
            self.assertTrue(current["ready"])

    def test_download_blocks_path_traversal_and_missing_files(self):
        for filename in ("../secret.json", "missing.json"):
            with self.subTest(filename=filename):
                with self.assertRaises(HTTPException) as raised:
                    download(filename)
                self.assertEqual(raised.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()

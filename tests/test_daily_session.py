import json
import tempfile
import unittest
from pathlib import Path

from services.daily_session import DailySessionStore


class DailySessionStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = DailySessionStore(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_save_and_resume(self):
        self.store.save(7, [11, 12, 11], 2, 1, {"AGAIN": 1, "GOOD": 1})
        value = self.store.load(7)
        self.assertEqual(value["pending"], [11, 12, 11])
        self.assertEqual(value["completed"], 1)
        self.assertEqual(value["ratings"]["AGAIN"], 1)
        self.assertIsNone(self.store.load(8))

    def test_clear(self):
        self.store.save(7, [2], 1, 0, {})
        self.store.clear(7)
        self.assertIsNone(self.store.load(7))

    def test_corrupt_save_is_ignored(self):
        path = Path(self.tmp.name) / "daily_review_7.json"
        path.write_text("{not-json", encoding="utf-8")
        self.assertIsNone(self.store.load(7))

    def test_invalid_or_wrong_deck_save_is_ignored(self):
        path = Path(self.tmp.name) / "daily_review_7.json"
        path.write_text(json.dumps({
            "version": 1, "set_id": 8, "pending": [2],
            "total": 1, "completed": 0, "ratings": {}
        }), encoding="utf-8")
        self.assertIsNone(self.store.load(7))


if __name__ == "__main__":
    unittest.main()

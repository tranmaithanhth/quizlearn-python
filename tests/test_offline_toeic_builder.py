import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.build_toeic_bilingual as builder


class FakeOfflineTranslator:
    calls = []

    def translate_batch(self, texts):
        self.calls.append(list(texts))
        return ["Bản dịch: " + text for text in texts]


class OfflineBuilderTests(unittest.TestCase):
    def test_resume_and_translate_missing_only(self):
        rows = [
            {
                "term": "invoice",
                "definition": "hóa đơn",
                "part_of_speech": "noun",
                "example": "Please pay the invoice.",
                "meaning_language": "vi",
            },
            {
                "term": "shipment",
                "definition": "A batch of goods being transported",
                "part_of_speech": "noun",
                "example": "The shipment arrived today.",
                "meaning_language": "en",
            },
        ]
        cache = {"Please pay the invoice within thirty days.": "Vui lòng thanh toán trong 30 ngày."}
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(builder, "CACHE", Path(folder) / "cache.json"), \
                 patch("services.offline_translation.OfflineTranslator", FakeOfflineTranslator):
                FakeOfflineTranslator.calls = []
                builder.prepare_offline_cache(rows, cache)
                self.assertEqual(len(FakeOfflineTranslator.calls), 1)
                texts = FakeOfflineTranslator.calls[0]
                self.assertNotIn("Please pay the invoice within thirty days.", texts)
                self.assertIn("A batch of goods being transported", texts)
                self.assertEqual(builder.load_cache(), cache)
                FakeOfflineTranslator.calls = []
                builder.prepare_offline_cache(rows, cache)
                self.assertEqual(FakeOfflineTranslator.calls, [])


if __name__ == "__main__":
    unittest.main()

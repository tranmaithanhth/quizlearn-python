import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import scripts.build_toeic_bilingual as builder


class TranslationRateLimitTests(unittest.TestCase):
    def test_429_stops_without_retry_and_preserves_cached_work(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(builder, "CACHE", Path(folder) / "cache.json"), \
                 patch.object(builder, "REQUEST_DELAY", 0), \
                 patch.object(builder, "_last_request_at", 0), \
                 patch.object(builder, "urlopen", side_effect=HTTPError(
                     url="https://translate.googleapis.com/",
                     code=429, msg="Too Many Requests",
                     hdrs={}, fp=None,
                 )) as mock_open:
                cache = {"The manager approved the request.": "Người quản lý đã phê duyệt yêu cầu."}
                with self.assertRaisesRegex(RuntimeError, "HTTP 429"):
                    builder.translate("Of great significance or value", cache)
                self.assertEqual(mock_open.call_count, 1)
                self.assertEqual(builder.load_cache(), cache)

    def test_cached_text_requires_no_network(self):
        with patch.object(builder, "urlopen") as mock_open:
            value = builder.translate("invoice", {"invoice": "hóa đơn"})
            self.assertEqual(value, "hóa đơn")
            mock_open.assert_not_called()


if __name__ == "__main__":
    unittest.main()

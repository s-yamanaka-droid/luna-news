import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "scripts" / "notify_slack.py"
SPEC = importlib.util.spec_from_file_location("notify_slack", SCRIPT)
notify_slack = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(notify_slack)


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"ok": True, "channel": "C123", "ts": "123.456"}


class NotifySlackTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "docs" / "news" / "2026-09-07").mkdir(parents=True)
        (self.root / "docs" / "weekly").mkdir(parents=True)
        (self.root / "logs").mkdir()
        (self.root / "docs" / "news" / "2026-09-07" / "articles.json").write_text(
            json.dumps(
                [
                    {
                        "source": "Primary",
                        "title": "A useful update",
                        "lede": "Summary",
                        "links": ["https://example.com/update"],
                    }
                ]
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temporary.cleanup()

    @mock.patch.dict(os.environ, {"SLACK_TOKEN": "test-token"}, clear=False)
    def test_send_records_receipt_and_skips_duplicate(self):
        session = mock.Mock()
        session.post.return_value = FakeResponse()
        with mock.patch.object(notify_slack, "ROOT", self.root):
            first = notify_slack.send_digest("2026-09-07", session=session)
            second = notify_slack.send_digest("2026-09-07", session=session)

        self.assertEqual("123.456", first["ts"])
        self.assertTrue(second["already_delivered"])
        session.post.assert_called_once()

    def test_payload_contains_target_and_article(self):
        payload = notify_slack.build_payload(
            "2026-09-07",
            "Trend",
            [{"source": "Primary", "title": "Update", "lede": "Summary", "link": "https://example.com"}],
        )
        encoded = json.dumps(payload, ensure_ascii=False)
        self.assertIn("2026-09-07", encoded)
        self.assertIn("Update", encoded)


if __name__ == "__main__":
    unittest.main()

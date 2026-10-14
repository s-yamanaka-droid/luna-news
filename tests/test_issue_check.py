"""Offline regression tests for the read-only issue acceptance check."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "issue_check.py"
spec = importlib.util.spec_from_file_location("issue_check", SCRIPT)
issue_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(issue_check)

DAY = "2026-10-14"
BASE = "https://nowonair.vercel.app"


def image_bytes(color):
    output = io.BytesIO()
    Image.new("RGB", (7, 5), color).save(output, format="PNG")
    return output.getvalue()


def page(path, extra="", story=False):
    schema = json.dumps({"@type": "NewsArticle", "datePublished": DAY,
                         "dateModified": DAY}) if story else ""
    social = "/assets/social.png" if story else "/assets/og-cover.png"
    return (f'<html><head><link rel="canonical" href="{BASE}{path}">'
            f'<meta property="og:url" content="{BASE}{path}">'
            f'<meta property="og:image" content="{BASE}{social}">'
            f'<script type="application/ld+json">{schema}</script></head>'
            f'<body><h1>A specific announcement</h1><time id="edition-time" datetime="{DAY}">{DAY}</time>'
            f'{extra}</body></html>').encode()


def files():
    article = {"title": "A specific announcement", "hero_image": "/assets/hero.png",
               "editorial_diagram": {"wide": "/assets/wide.png", "mobile": "/assets/mobile.png"},
               "social_image": "/assets/social.png"}
    return {
        "/health.json": (json.dumps({"latest_issue": DAY, "article_count": 1}).encode(), "application/json"),
        f"/news/{DAY}/articles.json": (json.dumps([article]).encode(), "application/json"),
        "/": (page("/", '<img src="/assets/hero.png">'), "text/html"),
        f"/news/{DAY}/": (page(f"/news/{DAY}/"), "text/html"),
        f"/articles/{DAY}/story-1/": (page(f"/articles/{DAY}/story-1/",
            '<picture><source srcset="/assets/mobile.png"><img src="/assets/wide.png"></picture>', True), "text/html"),
        "/assets/hero.png": (image_bytes("red"), "image/png"),
        "/assets/wide.png": (image_bytes("green"), "image/png"),
        "/assets/mobile.png": (image_bytes("blue"), "image/png"),
        "/assets/social.png": (image_bytes("yellow"), "image/png"),
    }


class Response:
    def __init__(self, payload, mime, url):
        self.body = io.BytesIO(payload)
        self.headers = {"Content-Type": mime, "Content-Length": str(len(payload))}
        self.status = 200
        self.url = url

    def read(self, size=-1):
        return self.body.read(size)

    def geturl(self):
        return self.url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class IssueCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.mapping = files()
        self.materialize()

    def materialize(self):
        for ref, (payload, _) in self.mapping.items():
            name = ref.lstrip("/") or "index.html"
            if ref.endswith("/") and ref != "/":
                name += "index.html"
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)

    def public(self):
        calls = []

        def get(url, timeout):
            calls.append((url, timeout))
            ref = url.removeprefix(BASE)
            if ref not in self.mapping:
                raise OSError("not found")
            payload, mime = self.mapping[ref]
            return Response(payload, mime, url)

        with patch.object(issue_check, "_open_url", side_effect=get):
            result = issue_check.check_public(BASE, DAY)
        return result, calls

    def test_local_and_public_accept_small_unique_images_and_return_real_hashes(self):
        local = issue_check.check_local(self.root, DAY)
        public, calls = self.public()
        self.assertTrue(local["ok"], local)
        self.assertTrue(public["ok"], public)
        self.assertEqual(local["articles_sha256"], public["articles_sha256"])
        self.assertEqual(local["asset_hashes"], public["asset_hashes"])
        self.assertEqual(len(local["asset_hashes"]), 4)
        self.assertEqual(local["asset_hashes"]["/assets/mobile.png"],
                         hashlib.sha256(self.mapping["/assets/mobile.png"][0]).hexdigest())
        self.assertTrue(all(0 < timeout <= 15 for _, timeout in calls))

    def test_rejects_stale_health_even_when_page_is_200(self):
        self.mapping["/health.json"] = (b'{"latest_issue":"2026-09-14","article_count":1}', "application/json")
        result, _ = self.public()
        self.assertFalse(result["ok"])
        self.assertIn("health:issue_date_mismatch", result["errors"])

    def test_rejects_missing_mobile_and_html_pretending_to_be_image(self):
        (self.root / "assets/mobile.png").unlink()
        self.assertFalse(issue_check.check_local(self.root, DAY)["ok"])
        self.mapping["/assets/mobile.png"] = (b"<html>fallback</html>", "text/html")
        result, _ = self.public()
        self.assertFalse(result["ok"])
        self.assertTrue(any("image_content_type" in error for error in result["errors"]))

    def test_rejects_broken_image_despite_image_content_type(self):
        self.mapping["/assets/mobile.png"] = (b"broken bytes", "image/png")
        self.materialize()
        self.assertFalse(issue_check.check_local(self.root, DAY)["ok"])
        self.assertFalse(self.public()[0]["ok"])

    def test_rejects_reused_bytes_in_all_four_roles(self):
        self.mapping["/assets/mobile.png"] = self.mapping["/assets/wide.png"]
        self.materialize()
        result = issue_check.check_local(self.root, DAY)
        self.assertFalse(result["ok"])
        self.assertTrue(any("image_reuse" in error for error in result["errors"]))

    def test_rejects_same_pixels_reencoded_as_different_bytes(self):
        output = io.BytesIO()
        Image.new("RGB", (7, 5), "green").save(output, format="PNG", compress_level=0)
        self.assertNotEqual(output.getvalue(), self.mapping["/assets/wide.png"][0])
        self.mapping["/assets/mobile.png"] = (output.getvalue(), "image/png")
        self.materialize()
        result = issue_check.check_local(self.root, DAY)
        self.assertFalse(result["ok"])
        self.assertTrue(any("image_reuse" in error for error in result["errors"]))

    def test_public_missing_asset_is_failure(self):
        del self.mapping["/assets/mobile.png"]
        result, _ = self.public()
        self.assertFalse(result["ok"])
        self.assertIn("article-1.mobile:http_read_failed", result["errors"])

    def test_timeout_is_reported_without_raw_exception_or_secret(self):
        with patch.object(issue_check, "_open_url", side_effect=TimeoutError("SECRET_MUST_NOT_APPEAR")):
            result = issue_check.check_public(BASE, DAY)
        self.assertFalse(result["ok"])
        self.assertNotIn("SECRET_MUST_NOT_APPEAR", json.dumps(result))

    def test_whole_check_has_a_deadline(self):
        with patch.object(issue_check, "MAX_CHECK_SECONDS", -1):
            result, calls = self.public()
        self.assertFalse(result["ok"])
        self.assertEqual(calls, [])
        self.assertIn("health:check_time_limit", result["errors"])

    def test_rejects_external_assets_and_encoded_traversal_without_fetching_them(self):
        for ref in ["https://other.example/secret.png", "/assets/%252e%252e/secret.png", "/assets/../secret.png"]:
            with self.subTest(ref=ref):
                key = f"/news/{DAY}/articles.json"
                data = json.loads(self.mapping[key][0])
                data[0]["hero_image"] = ref
                self.mapping[key] = (json.dumps(data).encode(), "application/json")
                result, calls = self.public()
                self.assertFalse(result["ok"])
                self.assertTrue(all(url.startswith(BASE + "/") for url, _ in calls))
                self.assertFalse(any("secret.png" in url for url, _ in calls))

    def test_rejects_symlink_escape_without_reading_outside_root(self):
        outside = Path(self.temp.name).parent / (self.root.name + "-outside.png")
        outside.write_bytes(image_bytes("black"))
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        target = self.root / "assets/mobile.png"
        target.unlink()
        target.symlink_to(outside)
        result = issue_check.check_local(self.root, DAY)
        self.assertFalse(result["ok"])
        self.assertTrue(any("path_outside_root" in error for error in result["errors"]))

    def test_rejects_article_canonical_og_and_date_mismatch(self):
        ref = f"/articles/{DAY}/story-1/"
        payload, mime = self.mapping[ref]
        self.mapping[ref] = (payload.replace(b"story-1/", b"story-2/").replace(b"2026-10-14", b"2026-09-14"), mime)
        result, _ = self.public()
        self.assertFalse(result["ok"])
        self.assertTrue(any("canonical" in error for error in result["errors"]))
        self.assertTrue(any("date" in error for error in result["errors"]))

    def test_rejects_same_date_html_from_a_different_candidate(self):
        ref = f"/articles/{DAY}/story-1/"
        payload, mime = self.mapping[ref]
        self.mapping[ref] = (payload.replace(b"A specific announcement", b"Old candidate headline"), mime)
        result, _ = self.public()
        self.assertFalse(result["ok"])
        self.assertIn("article-1:article_title_mismatch", result["errors"])

    def test_rejects_oversized_response_and_redirected_response(self):
        with patch.object(issue_check, "_open_url", return_value=Response(b"x" * 101, "application/json", BASE + "/health.json")), \
                patch.object(issue_check, "MAX_JSON_BYTES", 100):
            self.assertFalse(issue_check.check_public(BASE, DAY)["ok"])
        with patch.object(issue_check, "_open_url", return_value=Response(b"{}", "application/json", "https://other.example/health.json")):
            self.assertFalse(issue_check.check_public(BASE, DAY)["ok"])

    def test_cli_outputs_only_json_and_rejects_invalid_date(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), "--date", DAY], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])
        result = subprocess.run([sys.executable, str(SCRIPT), "--date", "2026-99-99"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(json.loads(result.stdout)["ok"])
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()

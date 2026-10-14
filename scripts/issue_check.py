"""Read-only technical acceptance for a dated Now on AIr issue.

This checks served files, article identity and image decoding. It does not verify
source facts, visual design quality, or whether a scheduled worker is running.
No credentials, API generation, notifications, or file writes are used.
"""
import argparse
from datetime import date, datetime
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import time
from urllib.parse import unquote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
import warnings
from zoneinfo import ZoneInfo

CANONICAL_BASE = "https://nowonair.vercel.app"
HTTP_TIMEOUT = 10
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_HTML_BYTES = 3 * 1024 * 1024
MAX_IMAGE_BYTES = 12 * 1024 * 1024
MAX_TOTAL_BYTES = 96 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
MAX_ARTICLES = 32
MAX_CHECK_SECONDS = 60
SCOPE = ("Technical file/identity/image checks only; source facts, visual design "
         "quality, and scheduled-worker operation are not verified.")


class CheckError(Exception):
    pass


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise CheckError("redirect_not_allowed")


def _open_url(url, timeout):
    request = Request(url, headers={"User-Agent": "NowOnAIr-IssueCheck/1.0",
                                    "Accept-Encoding": "identity"})
    return build_opener(_NoRedirect()).open(request, timeout=timeout)


def _valid_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise CheckError("invalid_date")
    try:
        date.fromisoformat(value)
    except ValueError:
        raise CheckError("invalid_date") from None
    return value


def _base(value):
    parsed = urlsplit(value)
    if (parsed.scheme not in ("https", "http") or not parsed.netloc or
            parsed.username or parsed.password or parsed.path not in ("", "/") or
            parsed.query or parsed.fragment or any(ord(c) < 33 for c in value)):
        raise CheckError("invalid_base_url")
    try:
        parsed.port
    except ValueError:
        raise CheckError("invalid_base_url") from None
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def _safe_path(value, base, asset=False):
    if not isinstance(value, str) or not value:
        raise CheckError("missing_asset_reference" if asset else "invalid_path")
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        if (parsed.scheme + "://" + parsed.netloc) != base:
            raise CheckError("external_reference")
    if parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise CheckError("unsafe_reference")
    path = parsed.path
    for _ in range(5):
        decoded = unquote(path)
        if decoded == path:
            break
        path = decoded
    if (not path.startswith("/") or path.startswith("//") or "\\" in path or
            "%" in path or any(ord(c) < 32 for c in path) or
            any(part in (".", "..") for part in path.split("/"))):
        raise CheckError("unsafe_path")
    if asset and not path.startswith("/assets/"):
        raise CheckError("asset_path_required")
    return path


class _Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.canonical, self.meta, self.edition, self.refs, self.schema = [], {}, [], [], []
        self.h1_count = 0
        self.h1_text = []
        self._in_h1 = False
        self._script = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h1":
            self.h1_count += 1
            self._in_h1 = True
        if tag == "link" and "canonical" in attrs.get("rel", "").split():
            self.canonical.append(attrs.get("href", ""))
        if tag == "meta":
            key = attrs.get("property", attrs.get("name", ""))
            self.meta.setdefault(key, []).append(attrs.get("content", ""))
        if tag == "time" and attrs.get("id") == "edition-time":
            self.edition.append(attrs.get("datetime", ""))
        if tag in ("img", "source"):
            if attrs.get("src"):
                self.refs.append(attrs["src"])
            for part in attrs.get("srcset", "").split(","):
                if part.strip():
                    self.refs.append(part.strip().split()[0])
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._script = []

    def handle_data(self, data):
        if self._in_h1:
            self.h1_text.append(data)
        if self._script is not None:
            self._script.append(data)

    def handle_endtag(self, tag):
        if tag == "h1":
            self._in_h1 = False
        if tag == "script" and self._script is not None:
            raw = "".join(self._script).strip()
            if raw:
                try:
                    self.schema.append(json.loads(raw))
                except ValueError:
                    self.schema.append(None)
            self._script = None


def _news_schemas(values):
    result = []
    for value in values:
        if isinstance(value, list):
            result.extend(_news_schemas(value))
        elif isinstance(value, dict):
            kinds = value.get("@type", [])
            if kinds == "NewsArticle" or isinstance(kinds, list) and "NewsArticle" in kinds:
                result.append(value)
            if isinstance(value.get("@graph"), list):
                result.extend(_news_schemas(value["@graph"]))
    return result


class _Check:
    def __init__(self, root, base, target):
        self.root = Path(root).resolve() if root is not None else None
        self.base = base
        self.target = target
        self.cache = {}
        self.total_bytes = 0
        self.deadline = time.monotonic() + MAX_CHECK_SECONDS
        self.raw_owners = {}
        self.pixel_owners = {}
        self.result = {"ok": False, "date": target, "article_count": 0,
                       "articles_sha256": None, "asset_hashes": {},
                       "errors": [], "scope": SCOPE}

    def error(self, label, code):
        # Labels are generated locally, never response bodies or exception text.
        message = f"{label}:{code}"
        if message not in self.result["errors"]:
            self.result["errors"].append(message)

    def read(self, path, kind):
        if time.monotonic() >= self.deadline:
            raise CheckError("check_time_limit")
        key = (path, kind)
        if key in self.cache:
            return self.cache[key]
        maximum = {"json": MAX_JSON_BYTES, "html": MAX_HTML_BYTES, "image": MAX_IMAGE_BYTES}[kind]
        mime = None
        if self.root is not None:
            rel = path.lstrip("/")
            if not rel or path.endswith("/"):
                rel += "index.html"
            local = (self.root / rel).resolve()
            if not local.is_relative_to(self.root):
                raise CheckError("path_outside_root")
            try:
                if not local.is_file():
                    raise CheckError("file_missing")
                if local.stat().st_size > maximum:
                    raise CheckError("response_too_large")
                with local.open("rb") as handle:
                    data = handle.read(maximum + 1)
            except OSError:
                raise CheckError("file_read_failed") from None
        else:
            url = self.base + path
            try:
                timeout = min(HTTP_TIMEOUT, max(0.1, self.deadline - time.monotonic()))
                with _open_url(url, timeout=timeout) as response:
                    if response.status != 200:
                        raise CheckError("http_status_not_200")
                    if response.geturl() != url:
                        raise CheckError("redirect_not_allowed")
                    mime = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
                    length = response.headers.get("Content-Length")
                    if length and (not length.isdigit() or int(length) > maximum):
                        raise CheckError("response_too_large")
                    # read1 returns available HTTP bytes, preventing a slow stream
                    # from extending an individual large read indefinitely.
                    read_chunk = getattr(response, "read1", response.read)
                    chunks, size = [], 0
                    while True:
                        if time.monotonic() >= self.deadline:
                            raise CheckError("check_time_limit")
                        chunk = read_chunk(min(65536, maximum + 1 - size))
                        if not chunk:
                            break
                        chunks.append(chunk)
                        size += len(chunk)
                        if size > maximum:
                            raise CheckError("response_too_large")
                    data = b"".join(chunks)
            except CheckError:
                raise
            except Exception:
                raise CheckError("http_read_failed") from None
            if kind == "json" and not (mime == "application/json" or mime.endswith("+json")):
                raise CheckError("json_content_type")
            if kind == "html" and mime not in ("text/html", "application/xhtml+xml"):
                raise CheckError("html_content_type")
            if kind == "image" and mime not in ("image/png", "image/jpeg", "image/webp", "image/gif"):
                raise CheckError("image_content_type")
        if len(data) > maximum:
            raise CheckError("response_too_large")
        self.total_bytes += len(data)
        if self.total_bytes > MAX_TOTAL_BYTES:
            raise CheckError("total_byte_limit")
        self.cache[key] = (data, mime)
        return data, mime

    def json(self, path, label):
        try:
            data, _ = self.read(path, "json")
            return json.loads(data), data
        except CheckError as exc:
            self.error(label, str(exc))
        except (ValueError, UnicodeError):
            self.error(label, "invalid_json")
        return None, None

    def page(self, path, label, story=False, social=None, title=None):
        try:
            data, _ = self.read(path, "html")
            parsed = _Page(data.decode("utf-8"))
        except CheckError as exc:
            self.error(label, str(exc))
            return None
        except (ValueError, UnicodeError):
            self.error(label, "invalid_html")
            return None
        expected = self.base + path
        if parsed.canonical != [expected]:
            self.error(label, "canonical_mismatch")
        if parsed.meta.get("og:url") != [expected]:
            self.error(label, "og_url_mismatch")
        if parsed.edition != [self.target]:
            self.error(label, "edition_date_mismatch")
        if story:
            if parsed.h1_count != 1:
                self.error(label, "article_heading_count")
            if not isinstance(title, str) or not title.strip() or (
                    " ".join("".join(parsed.h1_text).split()) != " ".join(title.split())):
                self.error(label, "article_title_mismatch")
            if social and parsed.meta.get("og:image") != [self.base + social]:
                self.error(label, "og_image_mismatch")
            schemas = _news_schemas(parsed.schema)
            if len(schemas) != 1:
                self.error(label, "article_schema_count")
            else:
                for key in ("datePublished", "dateModified"):
                    value = schemas[0].get(key)
                    if not isinstance(value, str) or value[:10] != self.target:
                        self.error(label, key + "_mismatch")
        return parsed

    def image(self, path, label):
        try:
            data, mime = self.read(path, "image")
            digest = hashlib.sha256(data).hexdigest()
            self.result["asset_hashes"][path] = digest
            from PIL import Image
            # Decoder warnings must not leak raw diagnostics into JSON-only CLI.
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                with Image.open(io.BytesIO(data)) as image:
                    fmt = image.format
                    width, height = image.size
                    if width <= 0 or height <= 0 or width * height > MAX_IMAGE_PIXELS:
                        raise CheckError("image_pixel_limit")
                    if getattr(image, "n_frames", 1) != 1:
                        raise CheckError("animated_image_unsupported")
                    image.verify()
                formats = {"PNG": ("image/png", (".png",)), "JPEG": ("image/jpeg", (".jpg", ".jpeg")),
                           "WEBP": ("image/webp", (".webp",)), "GIF": ("image/gif", (".gif",))}
                if fmt not in formats:
                    raise CheckError("image_format_unsupported")
                expected_mime, suffixes = formats[fmt]
                if not path.lower().endswith(suffixes) or mime and mime != expected_mime:
                    raise CheckError("image_format_mismatch")
                with Image.open(io.BytesIO(data)) as image:
                    image.load()
                    pixels = hashlib.sha256(f"{width}:{height}:".encode() + image.convert("RGBA").tobytes()).hexdigest()
            if digest in self.raw_owners or pixels in self.pixel_owners:
                raise CheckError("image_reuse")
            self.raw_owners[digest] = label
            self.pixel_owners[pixels] = label
        except CheckError as exc:
            self.error(label, str(exc))
        except ImportError:
            self.error(label, "image_decoder_unavailable")
        except Exception:
            self.error(label, "image_decode_failed")

    def run(self):
        health, _ = self.json("/health.json", "health")
        articles, raw = self.json(f"/news/{self.target}/articles.json", "articles")
        if raw is not None:
            self.result["articles_sha256"] = hashlib.sha256(raw).hexdigest()
        if not isinstance(articles, list) or not 1 <= len(articles) <= MAX_ARTICLES:
            self.error("articles", "article_list_required")
            return self.result
        self.result["article_count"] = len(articles)
        if not isinstance(health, dict) or health.get("latest_issue") != self.target:
            self.error("health", "issue_date_mismatch")
        if not isinstance(health, dict) or health.get("article_count") != len(articles):
            self.error("health", "article_count_mismatch")
        home = self.page("/", "home")
        self.page(f"/news/{self.target}/", "issue")
        for number, article in enumerate(articles, 1):
            label = f"article-{number}"
            if not isinstance(article, dict):
                self.error(label, "article_object_required")
                continue
            diagram = article.get("editorial_diagram") or {}
            if not isinstance(diagram, dict):
                diagram = {}
            refs = {"hero": article.get("hero_image"), "wide": diagram.get("wide"),
                    "mobile": diagram.get("mobile"), "social": article.get("social_image")}
            paths = {}
            for role, ref in refs.items():
                try:
                    path = _safe_path(ref, self.base, asset=True)
                    paths[role] = path
                    self.image(path, f"{label}.{role}")
                except CheckError as exc:
                    self.error(f"{label}.{role}", str(exc))
            page = self.page(f"/articles/{self.target}/story-{number}/", label,
                             story=True, social=paths.get("social"), title=article.get("title"))
            if page:
                for role in ("wide", "mobile"):
                    if paths.get(role) and paths[role] not in page.refs:
                        self.error(f"{label}.{role}", "not_referenced_in_article")
            if number == 1 and home and paths.get("hero") not in home.refs:
                self.error(f"{label}.hero", "not_referenced_in_home")
            if number == 1 and home and (
                    " ".join("".join(home.h1_text).split()) != " ".join(str(article.get("title", "")).split())):
                self.error("home", "featured_title_mismatch")
        self.result["ok"] = not self.result["errors"]
        return self.result


def _check(root, base, date_str):
    try:
        target = _valid_date(date_str)
        return _Check(root, _base(base), target).run()
    except CheckError as exc:
        return {"ok": False, "errors": [str(exc)], "article_count": 0,
                "articles_sha256": None, "asset_hashes": {}, "scope": SCOPE}
    except Exception:
        return {"ok": False, "errors": ["check_failed"], "article_count": 0,
                "articles_sha256": None, "asset_hashes": {}, "scope": SCOPE}


def check_local(root: Path, date_str: str) -> dict:
    """Read an existing docs directory; never creates or changes a file."""
    return _check(root, CANONICAL_BASE, date_str)


def check_public(base_url: str, date_str: str) -> dict:
    """GET one same-origin issue with bounded response sizes and no redirects."""
    return _check(None, base_url, date_str)


class _Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise CheckError("invalid_arguments")


def main(argv=None):
    parser = _Arguments(description=__doc__, add_help=False)
    parser.add_argument("--date", default=datetime.now(ZoneInfo("Asia/Tokyo")).date().isoformat())
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--root", type=Path)
    group.add_argument("--base-url")
    try:
        args = parser.parse_args(argv)
        _valid_date(args.date)
        if args.base_url:
            _base(args.base_url)
            result = check_public(args.base_url, args.date)
        else:
            root = args.root or Path(__file__).resolve().parents[1] / "docs"
            result = check_local(root, args.date)
    except CheckError:
        print(json.dumps({"ok": False, "errors": ["invalid_arguments"]}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

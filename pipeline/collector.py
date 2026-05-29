"""
VIGIL — Multi-Source Collector
RSS(329件) + API(HN/Reddit/GitHub/PH) を並列収集する高速コレクター。
researcher.py の fetch_latest を置き換え。
"""
import feedparser
import requests
import json
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

from feeds import RSS_FEEDS
from api_sources import fetch_api_sources

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

SKIP_TAGS = {"script", "style", "nav", "header", "footer",
             "aside", "form", "button", "noscript", "iframe"}

SEEN_PATH = Path.home() / "agents/cmo/x_agent/seen_urls.json"


def _load_seen() -> set:
    if not SEEN_PATH.exists():
        return set()
    try:
        data = json.loads(SEEN_PATH.read_text(encoding="utf-8"))
        return set(data.get("urls", []))
    except Exception:
        return set()


def _save_seen(seen: set):
    SEEN_PATH.write_text(
        json.dumps({"urls": sorted(seen), "updated": datetime.now().isoformat()},
                   ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def mark_seen(links: list[str]):
    seen = _load_seen()
    seen.update(l for l in links if l)
    _save_seen(seen)
    print(f"[seen] {len(seen)}件のURLを既読登録済み")


def _fetch_body(url: str, max_chars: int = 2500) -> str:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(SKIP_TAGS):
            tag.decompose()
        body = soup.find("article") or soup.find("main") or soup.body
        if not body:
            return ""
        return " ".join(body.get_text(" ", strip=True).split())[:max_chars]
    except Exception:
        return ""


def _fetch_one_feed(source: str, url: str, max_per_feed: int, seen: set,
                    fetch_body: bool) -> list[dict]:
    """1フィードを処理して記事リストを返す"""
    articles = []
    try:
        # feedparser にはタイムアウトがないので requests で取得してから parse
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            feed = feedparser.parse(resp.content)
        except requests.Timeout:
            return []
        except Exception:
            feed = feedparser.parse(url)  # フォールバック
        count = 0
        for entry in feed.entries[:max_per_feed * 3]:
            link = entry.get("link", "")
            if link and link in seen:
                continue
            body = _fetch_body(link) if fetch_body and link else ""
            articles.append({
                "source": source,
                "title": entry.get("title", ""),
                "summary": entry.get("summary", "")[:400],
                "link": link,
                "published": entry.get("published", ""),
                "body": body,
            })
            count += 1
            if count >= max_per_feed:
                break
    except Exception as e:
        log.debug(f"[SKIP] {source}: {e}")
    return articles


def fetch_all(max_per_feed: int = 2, fetch_body: bool = True,
              skip_seen: bool = True, max_workers: int = 30) -> list[dict]:
    """
    RSS 329件 + API 4ソースを並列収集。
    max_workers=30 で 329フィードを ~12秒で処理（直列だと10分超）。
    """
    seen = _load_seen() if skip_seen else set()
    all_articles = []

    # RSS を並列取得
    log.info(f"   RSS {len(RSS_FEEDS)}フィードを並列取得中...")
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_fetch_one_feed, name, url, max_per_feed, seen, fetch_body): name
            for name, url in RSS_FEEDS
        }
        done_count = 0
        for future in as_completed(futures):
            done_count += 1
            try:
                all_articles.extend(future.result())
            except Exception:
                pass
            if done_count % 50 == 0:
                log.info(f"   RSS {done_count}/{len(RSS_FEEDS)} 完了...")

    rss_count = len(all_articles)
    log.info(f"   RSS: {rss_count}件取得")

    # API ソース（HN, Reddit, GitHub Trending, Product Hunt）
    try:
        api_articles = fetch_api_sources(skip_seen=seen)
        all_articles.extend(api_articles)
        log.info(f"   API: {len(api_articles)}件取得")
    except Exception as e:
        log.warning(f"   API収集エラー: {e}")

    log.info(f"   合計: {len(all_articles)}件")
    return all_articles


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    articles = fetch_all(max_per_feed=1, fetch_body=False)
    print(f"\n収集件数: {len(articles)}")
    for a in articles[:5]:
        print(f"  [{a['source']}] {a['title']}")

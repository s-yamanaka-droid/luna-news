"""
VIGIL — Non-RSS API Sources
Hacker News / Reddit / GitHub Trending / Product Hunt から AI ニュースを収集。
返却形式は researcher.py の fetch_latest() と同一。
"""
import re
import logging
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

log = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

TIMEOUT = 10

# AI 関連キーワード（小文字で比較）
AI_KEYWORDS = re.compile(
    r"\b(ai|llm|gpt|claude|openai|anthropic|gemini|ml|"
    r"machine.?learning|deep.?learning|neural.?net|transformer|diffusion|"
    r"lang.?chain|rag|fine.?tun|lora|gguf|ollama|llama|mistral|"
    r"stable.?diffusion|midjourney|copilot|chatbot|agent)\b",
    re.IGNORECASE,
)

# GitHub Trending 用（description ベース）
GH_KEYWORDS = re.compile(
    r"\b(ai|ml|llm|model|transformer|diffusion|neural|"
    r"language.?model|deep.?learning|machine.?learning|"
    r"gpt|claude|gemini|agent|rag|embedding)\b",
    re.IGNORECASE,
)


# ── Hacker News ────────────────────────────────────────
def fetch_hackernews(skip_seen: set = None) -> list[dict]:
    """HN Top 50 から AI 関連記事を抽出"""
    skip_seen = skip_seen or set()
    articles = []

    resp = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json",
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    top_ids = resp.json()[:50]

    def _fetch_item(item_id: int) -> dict | None:
        r = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json",
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(_fetch_item, iid): iid for iid in top_ids}
        for fut in as_completed(futures):
            try:
                item = fut.result()
            except Exception:
                continue
            if not item or item.get("type") != "story":
                continue

            title = item.get("title", "")
            url = item.get("url", f"https://news.ycombinator.com/item?id={item['id']}")

            if url in skip_seen:
                continue
            if not AI_KEYWORDS.search(title):
                continue

            ts = item.get("time", 0)
            published = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat() if ts else ""

            articles.append({
                "source": "Hacker News",
                "title": title,
                "summary": f"Score: {item.get('score', 0)} | Comments: {item.get('descendants', 0)}",
                "link": url,
                "published": published,
                "body": "",
            })

    log.info(f"[HN] {len(articles)}件取得")
    return articles


# ── Reddit ─────────────────────────────────────────────
SUBREDDITS = [
    ("r/MachineLearning", 25),
    ("r/artificial", 25),
    ("r/LocalLLaMA", 25),
    ("r/ChatGPT", 15),
    ("r/ClaudeAI", 15),
]


def fetch_reddit(skip_seen: set = None) -> list[dict]:
    """Reddit AI 関連サブレディットを RSS フィードで取得（JSON API は 403 のため）"""
    skip_seen = skip_seen or set()
    articles = []

    try:
        import feedparser
    except ImportError:
        log.warning("[Reddit] feedparser がないためスキップ")
        return articles

    for sub, limit in SUBREDDITS:
        try:
            url = f"https://www.reddit.com/{sub}/hot/.rss?limit={limit}"
            feed = feedparser.parse(url, request_headers=HEADERS)

            for entry in feed.entries:
                link = entry.get("link", "")
                if link in skip_seen:
                    continue

                title = entry.get("title", "")
                summary = ""
                if entry.get("summary"):
                    s = BeautifulSoup(entry["summary"], "html.parser")
                    summary = s.get_text(" ", strip=True)[:400]

                articles.append({
                    "source": f"Reddit {sub}",
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "published": entry.get("published", ""),
                    "body": "",
                })
        except Exception as e:
            log.warning(f"[Reddit] {sub} 失敗: {e}")

    log.info(f"[Reddit] {len(articles)}件取得")
    return articles


# ── GitHub Trending ────────────────────────────────────
def fetch_github_trending(skip_seen: set = None) -> list[dict]:
    """GitHub Trending (daily) から AI 関連リポジトリを取得"""
    skip_seen = skip_seen or set()
    articles = []

    resp = requests.get(
        "https://github.com/trending?since=daily",
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    for row in soup.select("article.Box-row"):
        # リポジトリ名
        h2 = row.select_one("h2 a")
        if not h2:
            continue
        repo_path = h2.get("href", "").strip("/")
        link = f"https://github.com/{repo_path}"
        if link in skip_seen:
            continue

        # 説明文
        desc_tag = row.select_one("p")
        desc = desc_tag.get_text(strip=True) if desc_tag else ""

        # スター数
        star_tag = row.select_one("span.d-inline-block.float-sm-right")
        stars = star_tag.get_text(strip=True) if star_tag else ""

        # AI フィルタ（リポジトリ名 + 説明文）
        searchable = f"{repo_path} {desc}".lower()
        if not GH_KEYWORDS.search(searchable):
            continue

        articles.append({
            "source": "GitHub Trending",
            "title": repo_path,
            "summary": f"{desc} ({stars} stars today)" if stars else desc,
            "link": link,
            "published": datetime.now(tz=timezone.utc).isoformat(),
            "body": "",
        })

    log.info(f"[GitHub] {len(articles)}件取得")
    return articles


# ── Product Hunt ───────────────────────────────────────
def fetch_producthunt(skip_seen: set = None) -> list[dict]:
    """Product Hunt の RSS フィードから AI 関連プロダクトを取得"""
    skip_seen = skip_seen or set()
    articles = []

    try:
        import feedparser
        feed = feedparser.parse("https://www.producthunt.com/feed")

        for entry in feed.entries[:30]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", "")[:400]

            if link in skip_seen:
                continue

            searchable = f"{title} {summary}".lower()
            if not AI_KEYWORDS.search(searchable):
                continue

            articles.append({
                "source": "Product Hunt",
                "title": title,
                "summary": summary,
                "link": link,
                "published": entry.get("published", ""),
                "body": "",
            })
    except Exception as e:
        log.warning(f"[ProductHunt] 失敗: {e}")

    log.info(f"[PH] {len(articles)}件取得")
    return articles


# ── 統合関数 ───────────────────────────────────────────
def fetch_api_sources(skip_seen: set = None) -> list[dict]:
    """全 API 情報源から記事を収集し、RSS と同じ形式で返す"""
    skip_seen = skip_seen or set()
    all_articles = []

    fetchers = [
        ("Hacker News", fetch_hackernews),
        ("Reddit", fetch_reddit),
        ("GitHub Trending", fetch_github_trending),
        ("Product Hunt", fetch_producthunt),
    ]

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {
            pool.submit(fn, skip_seen): name for name, fn in fetchers
        }
        for fut in as_completed(futures, timeout=30):
            name = futures[fut]
            try:
                results = fut.result()
                all_articles.extend(results)
            except Exception as e:
                log.warning(f"[api_sources] {name} 失敗: {e}")

    log.info(f"[api_sources] 合計 {len(all_articles)}件取得")
    return all_articles


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    items = fetch_api_sources()
    for a in items:
        print(f"[{a['source']}] {a['title']}")
        print(f"  {a['link']}")
        print()
    print(f"合計: {len(items)}件")

"""
VIGIL — Main Pipeline
RSS(329) + API(HN/Reddit/GitHub/PH) → Gemini要約 → CSSカード → HTML → push
スライド画像生成廃止。CSSカードで直接表示。コスト $0。
"""
import sys
import logging
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from collector import fetch_all, mark_seen
from generator import generate_articles
from html_builder import build_daily_page, build_index, SITE_DIR
from deploy import git_push
from social_poster import post_dispatch

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / f"{datetime.now().strftime('%Y%m%d')}.log"),
    ],
)
log = logging.getLogger(__name__)


def _filter_by_pubdate(raw: list[dict], date_str: str) -> list[dict]:
    """バックフィル用：対象日の朝刊ウィンドウ（前日06:30〜当日06:30 JST）に
    公開された記事だけ残す。published が解析不能な記事は除外。"""
    from email.utils import parsedate_to_datetime
    from datetime import timedelta, timezone
    jst = timezone(timedelta(hours=9))
    day_end = datetime.strptime(date_str, "%Y-%m-%d").replace(
        hour=6, minute=30, tzinfo=jst)
    day_start = day_end - timedelta(hours=24)
    out = []
    for a in raw:
        pub = a.get("published", "")
        if not pub:
            continue
        try:
            dt = parsedate_to_datetime(pub)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except Exception:
            try:
                dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            except Exception:
                continue
        if day_start <= dt.astimezone(jst) < day_end:
            out.append(a)
    return out


def run(date_str: str = None, dry_run: bool = False, skip_slides: bool = False, skip_social: bool = False):
    today = datetime.now().strftime("%Y-%m-%d")
    backfill = date_str is not None and date_str != today
    date_str = date_str or today
    log.info(f"=== VIGIL {date_str}{' (backfill)' if backfill else ''} ===")

    # 1. 多層ソース収集（RSS 329件 + API 4ソース・並列）
    log.info("1. ソース収集（RSS 329 + HN/Reddit/GitHub/PH）")
    raw = fetch_all(max_per_feed=2, fetch_body=True)

    if backfill:
        raw = _filter_by_pubdate(raw, date_str)
        log.info(f"   [backfill] {date_str} の朝刊ウィンドウ内: {len(raw)}件")
        if len(raw) < 5:
            log.warning(f"   [backfill] 候補{len(raw)}件は少なすぎ → {date_str} は休刊のまま")
            return

    # 2. 記事要約（LLM_PROVIDER に従う・フォールバック連鎖付き）
    log.info("2. 記事生成")
    articles = generate_articles(raw)
    log.info(f"   {len(articles)}件生成")

    # 3. スライド画像生成（Codex CLI 並列・ChatGPT Plus サブスク内・API課金ゼロ）
    if not skip_slides:
        log.info("3. スライド画像生成（Codex CLI 並列・4 workers）")
        try:
            from slide_maker import generate_slides_parallel
            img_dir = SITE_DIR / "assets" / "images" / date_str
            success = generate_slides_parallel(articles[:8], img_dir, max_workers=2)  # Codex並列混線回避
            log.info(f"   {success}/{min(len(articles),8)}枚成功")
        except Exception as e:
            log.warning(f"   スライド生成失敗（処理は継続）: {e}")
    else:
        log.info("3. スライド画像生成スキップ（--skip-slides）")

    # 4. HTML生成
    log.info("4. HTML生成")

    # 記事データをJSONで保存（再ビルド時に使えるように）
    import json
    data_dir = SITE_DIR / "news" / date_str
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "articles.json").write_text(
        json.dumps(articles, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    daily_path = build_daily_page(date_str, articles)
    log.info(f"   {daily_path}")

    all_dates = sorted([d.name for d in (SITE_DIR / "news").iterdir() if d.is_dir()])
    index_path = build_index(all_dates, articles, date_str)
    log.info(f"   {index_path}")

    # 5. デプロイ
    if not dry_run:
        log.info("5. GitHub push")
        ok = git_push(f"dispatch: {date_str} — {len(articles)} items")
        log.info(f"   {'✓ 完了' if ok else '✗ 失敗'}")
    else:
        log.info("5. [DRY RUN] push スキップ")

    # 6. SNS投稿（Threads のみ / X は有料APIのためスキップ。backfill は旧ニュースなので投稿しない）
    if not dry_run and not skip_social and not backfill:
        log.info("6. SNS投稿（Threads）")
        post_dispatch(articles, date_str, post_x=False, post_threads=True)
    else:
        log.info("6. SNS投稿スキップ")

    # 7. 使用済みURLを登録（次回の重複スキップ用）
    # backfill では使った記事だけ登録（raw 全件登録すると当日分の候補を汚染する）
    used_links = [a.get("links", [""])[0] for a in articles if a.get("links")]
    if backfill:
        mark_seen(list(set(used_links)))
        log.info(f"   既読URL登録(backfill): {len(set(used_links))}件")
    else:
        raw_links = [r.get("link", "") for r in raw if r.get("link")]
        mark_seen(list(set(used_links + raw_links)))
        log.info(f"   既読URL登録: {len(set(used_links + raw_links))}件")

    log.info("=== 完了 ===")


if __name__ == "__main__":
    dry          = "--dry" in sys.argv
    skip_social  = "--skip-social" in sys.argv
    date_arg     = None
    if "--date" in sys.argv:
        i = sys.argv.index("--date")
        if i + 1 < len(sys.argv):
            date_arg = sys.argv[i + 1]
    run(date_str=date_arg, dry_run=dry, skip_social=skip_social)

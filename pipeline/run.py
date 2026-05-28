"""
VIGIL — Main Pipeline
RSS → Haiku要約 → Geminiスライド → HTML生成 → GitHub push
"""
import sys
import logging
from datetime import datetime
from pathlib import Path
import concurrent.futures

RESEARCHER_PATH = Path.home() / "agents/cmo/x_agent"
sys.path.insert(0, str(RESEARCHER_PATH))
sys.path.insert(0, str(Path(__file__).parent))

from researcher import fetch_latest, mark_seen
from generator import generate_articles
from slide_maker import generate_slide
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


def run(date_str: str = None, dry_run: bool = False, skip_slides: bool = False, skip_social: bool = False):
    date_str = date_str or datetime.now().strftime("%Y-%m-%d")
    log.info(f"=== VIGIL {date_str} ===")

    # 1. RSS収集（元記事本文も取得）
    log.info("1. RSS収集 + 本文取得")
    raw = fetch_latest(max_per_feed=4, fetch_body=True)
    log.info(f"   {len(raw)}件取得（本文付き）")

    # 2. Haiku要約
    log.info("2. 記事生成（Haiku）")
    articles = generate_articles(raw)
    log.info(f"   {len(articles)}件生成")

    # 3. スライド生成（Codex CLI・直列。並列は stream disconnect するため）
    if not skip_slides:
        log.info("3. スライド生成（Codex CLI）")
        img_dir = SITE_DIR / "assets" / "images" / date_str
        img_dir.mkdir(parents=True, exist_ok=True)

        results = []
        for i, a in enumerate(articles, 1):
            out = img_dir / f"topic_{i}.png"
            if out.exists():
                results.append((i, True)); continue
            ok = generate_slide(
                title=a["title"], category=a.get("category",""),
                source=a.get("source",""), summary=a.get("lede",""),
                keypoints=a.get("keypoints",[]), output_path=out,
            )
            log.info(f"   slide {i}/{len(articles)}: {'OK' if ok else 'FAIL'}")
            results.append((i, ok))
        ok_count = sum(1 for _, ok in results if ok)
        log.info(f"   {ok_count}/{len(articles)}枚生成完了")

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

    # 6. SNS投稿（Threads のみ / X は有料APIのためスキップ）
    if not dry_run and not skip_social:
        log.info("6. SNS投稿（Threads）")
        post_dispatch(articles, date_str, post_x=False, post_threads=True)
    elif dry_run:
        log.info("6. [DRY RUN] SNS投稿スキップ")
    else:
        log.info("6. SNS投稿スキップ（--skip-social）")

    # 7. 使用済みURLを登録（次回の重複スキップ用）
    used_links = [a.get("links", [""])[0] for a in articles if a.get("links")]
    raw_links  = [r.get("link","") for r in raw if r.get("link")]
    mark_seen(list(set(used_links + raw_links)))
    log.info(f"   既読URL登録: {len(set(used_links + raw_links))}件")

    log.info("=== 完了 ===")


if __name__ == "__main__":
    dry          = "--dry" in sys.argv
    skip         = "--skip-slides" in sys.argv
    skip_social  = "--skip-social" in sys.argv
    run(dry_run=dry, skip_slides=skip, skip_social=skip_social)

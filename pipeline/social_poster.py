"""
VIGIL — Social Poster
X (Twitter) と Threads に今日のディスパッチを自動投稿する

必要な環境変数:
  X:
    X_API_KEY
    X_API_SECRET
    X_ACCESS_TOKEN
    X_ACCESS_SECRET

  Threads:
    THREADS_USER_ID       (数字のユーザーID)
    THREADS_ACCESS_TOKEN  (長期アクセストークン)
"""
import os
import requests
import time

# ── 投稿テキスト生成 ──────────────────────────────────────────

def build_post_text(articles: list[dict], date_str: str, site_url: str, platform: str) -> str:
    """
    X / Threads 向けのテキストを生成する。
    platform: "x" | "threads"
    """
    limit = 270 if platform == "x" else 480

    top = articles[:5]
    lines = []
    for i, a in enumerate(top, 1):
        cat   = a.get("category", "")
        title = a.get("title", "")
        # 1行に収める
        line = f"{i}. [{cat}] {title}"
        if len(line) > 60:
            line = line[:57] + "…"
        lines.append(line)

    issue_num = date_str.replace("-", "")[4:]  # "0424"

    header = f"📰 VIGIL №{issue_num} — {date_str} 朝のAIニュース\n\n"
    body   = "\n".join(lines)
    footer = f"\n\n詳細 → {site_url}\n#AI #AIニュース #VIGIL"

    full = header + body + footer
    if len(full) > limit:
        # bodyを短縮
        body = "\n".join(lines[:3])
        full = header + body + footer
    return full


# ── X (Twitter) ──────────────────────────────────────────────

def post_to_x(text: str) -> dict:
    """tweepy で X に投稿する。成功時は {"id": ..., "text": ...} を返す。"""
    try:
        import tweepy
    except ImportError:
        raise RuntimeError("tweepy が未インストール: pip install tweepy")

    api_key    = os.environ["X_API_KEY"]
    api_secret = os.environ["X_API_SECRET"]
    at         = os.environ["X_ACCESS_TOKEN"]
    at_secret  = os.environ["X_ACCESS_SECRET"]

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=at,
        access_token_secret=at_secret,
    )
    resp = client.create_tweet(text=text)
    return {"id": resp.data["id"], "text": text}


# ── Threads ──────────────────────────────────────────────────

def post_to_threads(text: str) -> dict:
    """
    Threads Graph API でテキスト投稿する。
    ステップ1: コンテナ作成 → ステップ2: パブリッシュ
    """
    user_id = os.environ["THREADS_USER_ID"]
    token   = os.environ["THREADS_ACCESS_TOKEN"]
    base    = "https://graph.threads.net/v1.0"

    # Step 1: コンテナ作成
    r1 = requests.post(
        f"{base}/{user_id}/threads",
        params={
            "media_type":   "TEXT",
            "text":         text,
            "access_token": token,
        },
        timeout=30,
    )
    r1.raise_for_status()
    container_id = r1.json()["id"]

    # Threads は作成後少し待つ必要がある
    time.sleep(3)

    # Step 2: パブリッシュ
    r2 = requests.post(
        f"{base}/{user_id}/threads_publish",
        params={
            "creation_id":  container_id,
            "access_token": token,
        },
        timeout=30,
    )
    r2.raise_for_status()
    return {"id": r2.json()["id"], "text": text}


# ── メイン ───────────────────────────────────────────────────

def post_dispatch(
    articles: list[dict],
    date_str: str,
    site_url: str = "https://nowonair.vercel.app/",
    post_x: bool = True,
    post_threads: bool = True,
) -> dict:
    """
    X / Threads に投稿する。
    戻り値: {"x": {...} or None, "threads": {...} or None}
    """
    results = {}

    if post_x and os.environ.get("X_API_KEY"):
        text = build_post_text(articles, date_str, site_url, "x")
        try:
            results["x"] = post_to_x(text)
            print(f"  [X] 投稿完了: {results['x']['id']}")
        except Exception as e:
            print(f"  [X] エラー: {e}")
            results["x"] = None
    else:
        results["x"] = None
        if post_x:
            print("  [X] X_API_KEY 未設定、スキップ")

    if post_threads and os.environ.get("THREADS_ACCESS_TOKEN"):
        text = build_post_text(articles, date_str, site_url, "threads")
        try:
            results["threads"] = post_to_threads(text)
            print(f"  [Threads] 投稿完了: {results['threads']['id']}")
        except Exception as e:
            print(f"  [Threads] エラー: {e}")
            results["threads"] = None
    else:
        results["threads"] = None
        if post_threads:
            print("  [Threads] THREADS_ACCESS_TOKEN 未設定、スキップ")

    return results


if __name__ == "__main__":
    # テスト用：投稿テキストだけ確認（実際には投稿しない）
    sample = [
        {"category": "新モデル発表", "title": "ChatGPT Images 2.0 発表 — 文字・UIが崩れない画像モデル"},
        {"category": "ツール更新",   "title": "OpenAI Codex、MAU 4M突破+レート上限リセット"},
        {"category": "業界動向",     "title": "Cursor × SpaceX 提携 — Composerを現実の難コードで強化"},
        {"category": "新モデル発表", "title": "Googleが次世代TPU 8T/8iを発表"},
        {"category": "ツール更新",   "title": "GoogleがWorkspaceにAIインターン機能を実装"},
    ]
    for platform in ["x", "threads"]:
        text = build_post_text(sample, "2026-04-24",
                               "https://nowonair.vercel.app/", platform)
        print(f"=== {platform.upper()} ({len(text)}文字) ===")
        print(text)
        print()

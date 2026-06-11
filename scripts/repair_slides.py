"""図解の自己修復ステップ — md5重複・劣化(<500KB)の topic画像を検出し、
OpenAI API エンジンで再生成する。

Codex CLI（$0）を主としつつ、稀に出る並列混線の重複・Playwright fallback の
劣化画像だけを API（約$0.07/枚・確実）で打ち直す。通常は 0〜2枚/日 = ほぼ¥0。
daily.sh の [1.7] から呼ばれる。失敗しても配信は止めない（exit 0）。
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

MIN_SIZE = 500_000   # これ未満は Playwright fallback の劣化版とみなす


def main(date_str: str) -> None:
    img_dir = ROOT / "docs" / "assets" / "images" / date_str
    art_path = ROOT / "docs" / "news" / date_str / "articles.json"
    if not img_dir.exists() or not art_path.exists():
        print(f"[repair] {date_str} 対象なし")
        return

    articles = json.loads(art_path.read_text(encoding="utf-8"))
    seen: dict[str, Path] = {}
    bad: list[tuple[Path, str]] = []
    for p in sorted(img_dir.glob("topic_*.png")):
        size = p.stat().st_size
        h = hashlib.md5(p.read_bytes()).hexdigest()
        if size < MIN_SIZE:
            bad.append((p, f"劣化 {size}B"))
        elif h in seen:
            bad.append((p, f"md5重複 (={seen[h].name})"))
        else:
            seen[h] = p

    if not bad:
        print(f"[repair] {date_str} 全{len(seen)}枚 OK（重複・劣化なし）")
        return

    from slide_maker import _openai_api_generate
    for p, reason in bad:
        try:
            i = int(p.stem.split("_")[1])
        except ValueError:
            continue
        if i > len(articles):
            continue
        a = articles[i - 1]
        print(f"[repair] {p.name}: {reason} → API再生成")
        ok = _openai_api_generate(
            a.get("title", ""), a.get("category", ""), a.get("source", ""),
            a.get("lede", "") or a.get("summary", ""), a.get("keypoints", []), p,
        )
        print(f"[repair] {p.name}: {'OK' if ok else 'FAIL（次回 watchdog が検知）'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")

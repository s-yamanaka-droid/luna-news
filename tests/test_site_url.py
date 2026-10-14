"""公開URLが現行の正規URLにそろっていることを確認する。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STALE = (
    "s-yamanaka-droid.github.io/vigil-news",
    "s-yamanaka-droid.github.io/nowonair",
)


def test_no_stale_site_urls_in_code():
    hits = []
    for d in ("pipeline", "scripts"):
        for p in (ROOT / d).rglob("*"):
            if p.suffix not in {".py", ".sh"}:
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            hits += [f"{p.relative_to(ROOT)}: {s}" for s in STALE if s in text]
    assert not hits, "404の旧URLが残っています: " + ", ".join(hits)

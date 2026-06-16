"""topic_*.png → topic_*.webp 変換（表示用の軽量版を生成）。

PNG は番犬・repair・OG画像が使うので残し、ブラウザ表示だけ WebP に差し替える。
実測: 1.87MB PNG → 約190KB WebP（90%減）。詳細ページ 12.8MB → 約1.5MB。
冪等（既に最新のwebpがあればスキップ）。daily.sh の repair 後に当日分・補完日分を変換。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
QUALITY = 82


def convert_day(date_str: str) -> int:
    img_dir = ROOT / "docs" / "assets" / "images" / date_str
    if not img_dir.exists():
        print(f"[webp] {date_str} 画像ディレクトリなし")
        return 0
    from PIL import Image
    n = 0
    for png in sorted(img_dir.glob("topic_*.png")):
        webp = png.with_suffix(".webp")
        # 冪等: webp が png より新しければスキップ
        if webp.exists() and webp.stat().st_mtime >= png.stat().st_mtime:
            continue
        try:
            with Image.open(png) as im:
                im.save(webp, "WEBP", quality=QUALITY, method=6)
            n += 1
        except Exception as e:
            print(f"[webp] {png.name} 変換失敗: {e}")
    print(f"[webp] {date_str} 変換 {n}枚 (q{QUALITY})")
    return n


if __name__ == "__main__":
    convert_day(sys.argv[1] if len(sys.argv) > 1 else "")

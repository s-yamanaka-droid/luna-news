"""
Now on AIr — Slide Maker (OpenAI gpt-image-2 版)
日本語完璧・編集デザイン品質の図解生成。HTML→PNG版から切り替え。
"""
import os
import base64
from pathlib import Path

BRAND_NAME = os.environ.get("NOW_ON_BRAND", "AIr")
PRIMARY_COLOR = os.environ.get("NOW_ON_PRIMARY_COLOR", "#CE1141")
IMAGE_MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")

SLIDE_PROMPT_TEMPLATE = """A 16:9 editorial infographic news card slide. Magazine-quality, Japanese editorial design.

ARTICLE:
- Title (Japanese, render exactly): {title}
- Category (Japanese): {category}
- Source: {source}
- One-line summary (Japanese, render exactly): {summary}
- Key points (Japanese, render exactly as 3 or 4 separate boxes):
{keypoints}

DESIGN REQUIREMENTS (CRITICAL):
- Layout: top-to-bottom flow on pure white background (#FFFFFF)
- Top accent: thin horizontal line in primary color {primary_color} (3-4 px tall)
- Top-left: category label as a small SOLID PILL filled with {primary_color}, white text, uppercase, compact monospace style
- Top-right: brand mark "Now on {brand}" with the leading "{brand_main}" in {primary_color} bold and the trailing "{brand_sub}" in muted gray smaller
- Center: the article TITLE in large bold Japanese type (Noto Sans JP weight 900), 2-3 lines max, black #111
- Below title: the SUMMARY in a thin-bordered box, smaller Japanese serif
- Lower half: 3 to 4 ICON BOXES laid out horizontally, each containing:
    * A unique flat MINIMAL LINE ICON in {primary_color} that visually represents the key point's concept (gear, network nodes, lock, chart, briefcase, building, AI robot, document, arrow, etc.) — every box has a DIFFERENT icon
    * A small number badge (01, 02, 03, 04) in the top-right corner of each box
    * The Japanese key point text BELOW the icon, 1-2 lines, weight 700
    * Each box has a 1px thin gray border and {primary_color} top accent line
- Bottom-right: source badge "SOURCE: {source}" in monospace uppercase

VISUAL STYLE:
- Strictly black / white / {primary_color} only (allow medium gray for secondary text)
- No gradients, no shadows, no pastels, no photorealistic imagery
- Editorial / Swiss design / magazine feel
- Plenty of whitespace, refined typography hierarchy
- Render Japanese text crisply and correctly — DO NOT garble Japanese characters
- Render numbers and English crisply"""


def _build_prompt(title, category, source, summary, keypoints):
    kp_text = "\n".join(f"  {i+1}. {k}" for i, k in enumerate(keypoints[:4]))
    return SLIDE_PROMPT_TEMPLATE.format(
        title=title, category=category, source=source,
        summary=summary[:160], keypoints=kp_text,
        primary_color=PRIMARY_COLOR,
        brand=BRAND_NAME,
        brand_main=BRAND_NAME[:-1],
        brand_sub=BRAND_NAME[-1],
    )


def generate_slide(
    title: str,
    category: str,
    source: str,
    summary: str,
    keypoints: list[str],
    output_path: Path,
    size: str = "1536x1024",  # 16:9
) -> bool:
    """OpenAI gpt-image-2 で 1536x1024 の図解スライドを生成"""
    from openai import OpenAI
    client = OpenAI()
    prompt = _build_prompt(title, category, source, summary, keypoints)
    try:
        resp = client.images.generate(
            model=IMAGE_MODEL,
            prompt=prompt,
            size="1536x1024",
            n=1,
        )
        img_b64 = resp.data[0].b64_json
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(base64.b64decode(img_b64))
        return True
    except Exception as e:
        print(f"  [{IMAGE_MODEL}] error: {e}")
        return False


if __name__ == "__main__":
    out = Path("/tmp/test_slide_img2.png")
    ok = generate_slide(
        title="OpenAI、Gartnerが評価する企業向けコーディングエージェントのリーダーに",
        category="業界動向",
        source="OpenAI Blog",
        summary="OpenAIがGartnerのマジック・クアドラントでリーダー選出。Codexが企業導入を牽引。",
        keypoints=[
            "Codexが企業での利用拡大を実現",
            "週に400万人以上がCodexを使用",
            "GPT-5.5で生産性向上",
            "企業ソフトウェア開発の強化",
        ],
        output_path=out,
    )
    print(f"生成: {ok} → {out}")

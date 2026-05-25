"""
Now on AIr — Slide Maker (OpenAI gpt-image-2 版)
リッチ図解 + 日本語完璧。quality 切替で品質/コスト調整可能。
"""
import os
import base64
from pathlib import Path

BRAND_NAME = os.environ.get("NOW_ON_BRAND", "AIr")
PRIMARY_COLOR = os.environ.get("NOW_ON_PRIMARY_COLOR", "#CE1141")
IMAGE_MODEL = os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")
IMAGE_QUALITY = os.environ.get("OPENAI_IMAGE_QUALITY", "medium")  # low / medium / high

SLIDE_PROMPT_TEMPLATE = """A 16:9 editorial INFOGRAPHIC news card slide, magazine-quality Japanese editorial design with RICH ILLUSTRATED scenes.

ARTICLE DATA:
- Title (render exactly in Japanese): {title}
- Category (render exactly in Japanese): {category}
- Summary (render exactly in Japanese): {summary}
- Source: {source}
- Key points (each becomes one illustrated box, render Japanese exactly):
{keypoints}

LAYOUT (top to bottom, on pure white #FFFFFF):
1. THIN top border line in {primary_color} (3 px tall)
2. TOP-LEFT: solid filled pill in {primary_color} with white uppercase category text "{category}"
3. TOP-RIGHT: brand mark "Now on {brand}" — "{brand_main}" in {primary_color} bold larger, "{brand_sub}" in muted gray smaller
4. CENTER: the article TITLE in very large bold black Japanese type, 2-3 lines max
5. BELOW title: the SUMMARY in a thin-bordered horizontal box, smaller Japanese
6. LOWER HALF: 3 to 4 ILLUSTRATED CONCEPT BOXES side-by-side. Each box contains:
   a. A unique RICH ILLUSTRATED SCENE (NOT a flat single icon) combining 2-4 visual elements that represent the key point — e.g. building + dollar sign + arrows, AI chip + network nodes + person, cogs + chart + briefcase, lock + cloud + people, etc. Use {primary_color} for accents, black line work, subtle gray fills.
   b. Number badge "01" "02" "03" "04" in top-right corner of the box (filled {primary_color} background, white text)
   c. A BOLD black Japanese label (8-12 chars) below the illustration
   d. A small Japanese sub-label (10-16 chars) under the bold label
   e. Thin gray border around the box, with {primary_color} top accent stripe
7. BOTTOM-RIGHT: "Source: {source}" badge with thin border

VISUAL STYLE:
- Strictly limited palette: pure white background, black for type, {primary_color} as primary accent, light gray for secondary lines
- Magazine editorial / Swiss design feel — refined, not amateurish
- Generous whitespace
- Each illustrated box must show a DIFFERENT visual scene (no duplicate icons)
- Render Japanese characters PERFECTLY — no garbled text, no random shapes
- Numbers, English words, percentages must render crisply
- No gradients, no photorealism, no pastels, no dark backgrounds

Output an image that looks like a high-end Japanese magazine infographic page."""


def _build_prompt(title, category, source, summary, keypoints):
    kp_text = "\n".join(f"   {i+1}. {k}" for i, k in enumerate(keypoints[:4]))
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
    size: str = "1536x1024",
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
            quality=IMAGE_QUALITY,
            n=1,
        )
        img_b64 = resp.data[0].b64_json
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(base64.b64decode(img_b64))
        return True
    except Exception as e:
        print(f"  [{IMAGE_MODEL}/{IMAGE_QUALITY}] error: {e}")
        return False


if __name__ == "__main__":
    # 3 quality レベル比較
    import sys
    sample = {
        "title": "OpenAI、企業向けAI導入子会社「DeployCo」を立ち上げ──40億ドル調達",
        "category": "業界動向",
        "source": "OpenAI Blog",
        "summary": "OpenAI傘下のDeployCo、企業向けAI導入コンサルを開始。40億ドル超調達、Palantir流現地駐在型展開。",
        "keypoints": [
            "巨額投資で設立 TPG主導で40億ドル超調達",
            "現地駐在型導入 顧客データとAIを統合",
            "統合が競争力 ワークフロー設計で差別化",
            "戦略的フィードバック 現場知見をモデル開発へ",
        ],
    }
    for q in (sys.argv[1:] or ["low", "medium", "high"]):
        os.environ["OPENAI_IMAGE_QUALITY"] = q
        # 再import で IMAGE_QUALITY 更新
        import importlib, sys as _sys
        if "pipeline.slide_maker" in _sys.modules:
            del _sys.modules["pipeline.slide_maker"]
        out = Path(f"/tmp/test_slide_img2_{q}.png")
        ok = generate_slide(
            title=sample["title"], category=sample["category"],
            source=sample["source"], summary=sample["summary"],
            keypoints=sample["keypoints"], output_path=out,
        )
        # quality を強制適用するため re-call
        from openai import OpenAI
        client = OpenAI()
        resp = client.images.generate(
            model=IMAGE_MODEL,
            prompt=_build_prompt(sample["title"], sample["category"], sample["source"], sample["summary"], sample["keypoints"]),
            size="1536x1024", quality=q, n=1,
        )
        out.write_bytes(base64.b64decode(resp.data[0].b64_json))
        print(f"  quality={q}: {out}")

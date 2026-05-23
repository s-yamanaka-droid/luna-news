"""
Now on AIr — Slide Maker
Gemini 3.1 Flash Image Preview APIで各記事のスライド画像を生成する
"""
import os
import base64
import requests
import time
from pathlib import Path

API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_ID = "gemini-3.1-flash-image-preview"
API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

SLIDE_PROMPT_TEMPLATE = """
Create a 16:9 INFOGRAPHIC slide for the following AI news article.
This must be a VISUAL DIAGRAM with icons and illustrations — NOT a text-only slide.

ARTICLE:
Title: {title}
Category: {category}
Source: {source}
Summary: {summary}
Key Points:
{keypoints}

CRITICAL — INFOGRAPHIC REQUIREMENT (MOST IMPORTANT):
The slide MUST contain VISUAL DIAGRAMS that illustrate the key concepts.
DO NOT make a text-only slide with bullet points.

Required visual elements:
- 3 to 4 ICON/ILLUSTRATION BOXES arranged horizontally in the lower half
- Each box illustrates one key concept with:
  * A custom ICON or ILLUSTRATION (e.g., gear with chip for "engine", network nodes for "integration",
    lock for "security", arrow with clock for "speed", cloud for "cloud", graph for "growth", robot for "AI agent", etc.)
  * A short Japanese label below the icon (4-10 chars, e.g., "Codex駆動エージェント", "複数ツール連携", "クラウド実行", "WebSockets活用")
  * A one-line description below the label (8-15 chars in Japanese)
- Each icon box has a thin red border and small red number badge (1, 2, 3, 4) in the top-right corner
- Icons should be flat, minimal, geometric — NOT photorealistic — using black/red/gray with white background

LAYOUT (top to bottom):
1. TOP: Category label in red (top-left) + "Now on AIr" brand mark (top-right)
2. UPPER MIDDLE: Article TITLE — large, bold, black, 2-3 lines max
3. MIDDLE: A compact 1-line summary in a thin-bordered box (the "lede")
4. LOWER HALF (THE INFOGRAPHIC): 3-4 ICON BOXES side-by-side, each with icon + label + brief description
5. BOTTOM-RIGHT: Source badge ("Source: {source}")

DESIGN SYSTEM:
- Background: Pure white (#FFFFFF)
- Primary accent: Estate Brown (#6D4C41) — borders, badges, category label, accents
- Black (#0D0D0D) for main text
- Gray (#888) for secondary text
- Typography: Heavy condensed sans-serif for headline, clean sans-serif for labels, monospace for metadata
- NO pastels, NO dark backgrounds, NO gradients, NO photorealistic imagery
- Clean editorial infographic feel — like a magazine explainer graphic
- Japanese text rendered clearly and crisply

REMEMBER: The user has explicitly rejected text-only slides. The icon/illustration boxes
in the lower half are MANDATORY. Show, don't just tell.
"""


def generate_slide(
    title: str,
    category: str,
    source: str,
    summary: str,
    keypoints: list[str],
    output_path: Path,
    size: str = "2K",
) -> bool:
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY が未設定です")

    kp_text = "\n".join(f"- {kp}" for kp in keypoints[:5])
    prompt = SLIDE_PROMPT_TEMPLATE.format(
        title=title, category=category, source=source,
        summary=summary[:300], keypoints=kp_text,
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": "16:9",
                "imageSize": size,
            },
            "thinkingConfig": {
                "thinkingLevel": "High",
                "includeThoughts": False,
            },
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ],
    }

    url = f"{API_BASE}/{MODEL_ID}:generateContent?key={API_KEY}"

    for attempt in range(3):
        try:
            resp = requests.post(url, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()

            for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                if "inlineData" in part:
                    img_bytes = base64.b64decode(part["inlineData"]["data"])
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(img_bytes)
                    return True

        except Exception as e:
            print(f"  [attempt {attempt+1}/3] Gemini error: {e}")
            if attempt < 2:
                time.sleep(5 * (attempt + 1))

    # Gemini が全失敗 → OpenAI gpt-image-1 にフォールバック
    print("  [fallback] OpenAI gpt-image-1 で再試行（日本語文字化け回避モード）")
    try:
        return _openai_image_fallback(prompt, output_path, title=title)
    except Exception as e:
        print(f"  [fallback] OpenAI失敗: {e}")
        return False


OPENAI_IMAGE_PROMPT = """Create a 16:9 minimalist editorial INFOGRAPHIC for a news topic.

TOPIC CONTEXT (do NOT render this Japanese text in the image — use it only to choose appropriate icons):
{title}

CRITICAL DESIGN RULES (this is the most important part):
- ABSOLUTELY NO Japanese characters anywhere in the image. NO kanji, NO hiragana, NO katakana.
- Use ONLY simple ENGLISH words if any text is needed (1-3 word labels max, e.g., "MARKET", "AI", "GROWTH", "DATA").
- Prefer pure icons/symbols over any text. The image should communicate visually.
- If you cannot render text perfectly, render NO text at all — pure icons only.

VISUAL STYLE:
- Background: pure white (#FFFFFF)
- Primary accent color: #CE1141 (Chicago Red) — for borders, accents, key shapes
- Secondary: black (#0D0D0D) for outlines
- 3 to 4 icon boxes arranged horizontally, each with a flat minimalist icon (gear, building, chart, arrow, lock, person, etc.)
- Each box has a thin red border, a small numbered badge (1, 2, 3, 4) in the corner
- A thick red horizontal rule at the top
- A bold red vertical accent bar on the left edge
- Style: flat geometric, athletic, magazine editorial — like a sports brand applied to news graphics

NO photorealistic imagery. NO gradients. NO pastels. NO dark backgrounds. NO Japanese text. EVER."""


def _openai_image_fallback(prompt: str, output_path, title: str = "") -> bool:
    """OpenAI gpt-image-1 で 16:9 図解を生成（日本語文字化け回避版）"""
    from openai import OpenAI
    client = OpenAI()
    # 日本語入りの長文プロンプトをそのまま渡すと文字化け頻発
    # → OpenAI 専用にアイコン主体・英語ラベル限定のプロンプトに置換
    safe_prompt = OPENAI_IMAGE_PROMPT.format(title=title or "news topic")
    resp = client.images.generate(
        model="gpt-image-1",
        prompt=safe_prompt,
        size="1536x1024",
        n=1,
    )
    img_b64 = resp.data[0].b64_json
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(img_b64))
    return True


if __name__ == "__main__":
    out = Path("/tmp/test_slide.png")
    ok = generate_slide(
        title="OpenAI Codex 4M MAU突破",
        category="ツール更新",
        source="@sama",
        summary="CodexのMAUが400万人に到達。わずか2週間で3Mから4Mへ急増。",
        keypoints=["MAU 400万人到達", "2週間で100万人増", "レートリミット緩和を即時発表"],
        output_path=out,
    )
    print(f"生成: {ok} → {out}")

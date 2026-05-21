"""
LLM 抽象レイヤー — OpenAI (gpt-4o-mini) を優先、Anthropic フォールバック。
Anthropic のクレジット切れで配信が止まったため、OpenAI を主に切替。
"""
import os
import re

PROVIDER = os.environ.get("LLM_PROVIDER", "openai").lower()


def chat_json(system: str, user: str, max_tokens: int = 4000, model: str | None = None):
    """システム+ユーザープロンプトを送り、本文テキストを返す（JSON抽出は呼び出し側）"""
    if PROVIDER == "anthropic":
        return _anthropic(system, user, max_tokens, model or "claude-haiku-4-5-20251001")
    return _openai(system, user, max_tokens, model or "gpt-4o-mini")


def _openai(system: str, user: str, max_tokens: int, model: str) -> str:
    from openai import OpenAI
    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        max_completion_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content or ""


def _anthropic(system: str, user: str, max_tokens: int, model: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text


def extract_json(text: str, kind: str = "array") -> str:
    """LLM出力からJSON部分を抽出し、末尾カンマも修復"""
    text = text.strip()
    if kind == "array":
        start = text.find("[")
        end = text.rfind("]") + 1
    else:
        start = text.find("{")
        end = text.rfind("}") + 1
    raw = text[start:end] if start >= 0 and end > start else text
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    return raw

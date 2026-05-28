"""
LLM 抽象レイヤー — Codex CLI（ChatGPT Plus・API課金ゼロ）を優先。
OpenAI API / Anthropic にも切替可能。
"""
import os
import re
import subprocess

PROVIDER = os.environ.get("LLM_PROVIDER", "codex").lower()
CODEX_BIN = os.environ.get("CODEX_BIN", "/opt/homebrew/bin/codex")


def chat_json(system: str, user: str, max_tokens: int = 4000, model: str | None = None):
    """システム+ユーザープロンプトを送り、本文テキストを返す（JSON抽出は呼び出し側）"""
    if PROVIDER == "anthropic":
        return _anthropic(system, user, max_tokens, model or "claude-haiku-4-5-20251001")
    if PROVIDER == "openai":
        return _openai(system, user, max_tokens, model or "gpt-4o-mini")
    return _codex(system, user)


def _codex(system: str, user: str) -> str:
    """Codex CLI 経由（ChatGPT Plus 課金・API課金ゼロ）。JSONのみ出力させる。"""
    prompt = (
        f"{system}\n\n{user}\n\n"
        "【最重要】出力はJSONのみ。説明文・マークダウン記号(```)・前置きは一切禁止。"
        "JSONテキストだけを返すこと。ファイル作成も不要、標準出力にJSONを書くだけ。"
    )
    proc = subprocess.run(
        [CODEX_BIN, "exec", "--skip-git-repo-check", prompt],
        cwd="/tmp", capture_output=True, text=True, timeout=300,
    )
    out = proc.stdout
    # codex exec は最後に「tokens used\nN\n<最終回答>」を出す。最終回答だけ取り出す
    if "tokens used" in out:
        tail = out.rsplit("tokens used", 1)[1]
        # 次行(数値)以降が回答本体
        lines = tail.splitlines()
        out = "\n".join(lines[2:]) if len(lines) > 2 else tail
    return out


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

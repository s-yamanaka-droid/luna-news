"""
LLM 抽象レイヤー — Claude Code CLI をデフォルトに使用（サブスク内・API課金ゼロ）。
OpenAI / Anthropic API にもフォールバック切替可能。
"""
import os
import re

PROVIDER = os.environ.get("LLM_PROVIDER", "openai").lower()


def chat_json(system: str, user: str, max_tokens: int = 4000, model: str | None = None):
    """システム+ユーザープロンプトを送り、本文テキストを返す（JSON抽出は呼び出し側）"""
    if PROVIDER == "codex":
        return _codex(system, user)
    if PROVIDER == "claude":
        return _claude_code(system, user)
    if PROVIDER == "anthropic":
        return _anthropic(system, user, max_tokens, model or "claude-haiku-4-5-20251001")
    if PROVIDER == "openai":
        return _openai(system, user, max_tokens, model or "gpt-4o-mini")
    if PROVIDER == "gemini":
        return _gemini(system, user, max_tokens, model or "gemini-2.5-flash")
    raise ValueError(f"Unknown LLM_PROVIDER: {PROVIDER}")


def _codex(system: str, user: str) -> str:
    """Codex CLI 経由（ChatGPT Plus サブスク内・API課金ゼロ）"""
    import subprocess
    prompt = f"{system}\n\n{user}"
    proc = subprocess.run(
        ["/opt/homebrew/bin/codex", "exec", "--skip-git-repo-check",
         "--sandbox", "read-only", prompt],
        capture_output=True, text=True, timeout=300,
    )
    if proc.returncode != 0:
        err = proc.stderr or proc.stdout[:300]
        raise RuntimeError(f"codex CLI error (rc={proc.returncode}): {err[:300]}")
    # codex stdout には進捗ログとモデル出力が混ざるので、最後の構造化ブロックを抽出
    return proc.stdout


def _claude_code(system: str, user: str) -> str:
    """Claude Code CLI 経由（サブスク内・API課金ゼロ）"""
    import subprocess
    prompt = f"{system}\n\n{user}"
    # 長文プロンプトは stdin パイプ経由で渡す（引数長制限回避）
    proc = subprocess.run(
        ["claude", "-p", "--output-format", "text"],
        input=prompt,
        capture_output=True, text=True, timeout=180,
    )
    if proc.returncode != 0:
        # stderr が空なら stdout にエラーが出てる可能性
        err = proc.stderr or proc.stdout[:300]
        raise RuntimeError(f"claude CLI error (rc={proc.returncode}): {err[:300]}")
    return proc.stdout


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


def _gemini(system: str, user: str, max_tokens: int, model: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    m = genai.GenerativeModel(model)
    resp = m.generate_content(
        f"{system}\n\n{user}",
        generation_config=genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=0.3,
        ),
    )
    return resp.text


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

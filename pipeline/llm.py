"""
LLM 抽象レイヤー — Codex CLI をデフォルトに使用（ChatGPT Plus サブスク内・API課金ゼロ）。
プロバイダ失敗時は自動フォールバック連鎖（codex → claude → openai）。

2026-06-10 自己修復化:
- 6/6 Gemini SUSPENDED / 6/7-6/8 claude残高ゼロ / 6/10 codex timeout と
  単一プロバイダ依存の事故が4連発したため、chat_json はチェーン全体を試す。
"""
import logging
import os
import re
import shutil

PROVIDER = os.environ.get("LLM_PROVIDER", "codex").lower()
# 主プロバイダ失敗時に順に試す（重複は自動除去）
FALLBACK_CHAIN = [p.strip() for p in os.environ.get(
    "LLM_FALLBACK_CHAIN", "codex,claude,openai").lower().split(",") if p.strip()]
CODEX_TEXT_TIMEOUT = int(os.environ.get("CODEX_TEXT_TIMEOUT", "900"))   # Stage2 巨大プロンプト対応
# codex は npm 版 / homebrew 版が併存し、古い方は新モデル(gpt-5.6-sol)で 400 になる。
# PATH 上の最新を優先し、homebrew 固定パスは最後の保険にする（2026-08-04 6日間停止の真因）。
CODEX_BIN = os.environ.get("CODEX_BIN") or shutil.which("codex") or "/opt/homebrew/bin/codex"

log = logging.getLogger(__name__)


def chat_json(system: str, user: str, max_tokens: int = 4000, model: str | None = None):
    """システム+ユーザープロンプトを送り、本文テキストを返す（JSON抽出は呼び出し側）。
    主プロバイダ → フォールバック連鎖の順で試し、全滅時のみ例外。"""
    chain = [PROVIDER] + [p for p in FALLBACK_CHAIN if p != PROVIDER]
    last_err: Exception | None = None
    for prov in chain:
        try:
            text = _dispatch(prov, system, user, max_tokens, model)
            if text and text.strip():
                if prov != PROVIDER:
                    log.warning(f"[llm] fallback成功: {PROVIDER} → {prov}")
                return text
            raise RuntimeError(f"{prov}: empty response")
        except Exception as e:
            last_err = e
            log.warning(f"[llm] provider={prov} 失敗: {str(e)[:200]} → 次を試行")
    raise RuntimeError(f"[llm] 全プロバイダ失敗 (chain={chain}): {last_err}")


def _dispatch(provider: str, system: str, user: str, max_tokens: int, model: str | None) -> str:
    if provider == "codex":
        return _codex(system, user)
    if provider == "claude":
        return _claude_code(system, user)
    if provider == "anthropic":
        return _anthropic(system, user, max_tokens, model or "claude-haiku-4-5-20251001")
    if provider == "openai":
        return _openai(system, user, max_tokens, model or "gpt-4o-mini")
    if provider == "gemini":
        return _gemini(system, user, max_tokens, model or "gemini-2.5-flash")
    raise ValueError(f"Unknown LLM provider: {provider}")


def _codex(system: str, user: str) -> str:
    """Codex CLI 経由（ChatGPT Plus サブスク内・API課金ゼロ）。
    Stage2 のような巨大プロンプトは gpt-5 の思考時間が長いので timeout は 900s。"""
    import subprocess
    prompt = f"{system}\n\n{user}"
    # stdin=DEVNULL: 引数でprompt渡しても codex が stdin 待ちでハングする現象を防ぐ
    # （6/14 朝刊失敗の codex 側真因「Reading additional input from stdin」対策）
    proc = subprocess.run(
        [CODEX_BIN, "exec", "--skip-git-repo-check",
         "--sandbox", "read-only", prompt],
        stdin=subprocess.DEVNULL,
        capture_output=True, text=True, timeout=CODEX_TEXT_TIMEOUT,
    )
    if proc.returncode != 0:
        err = proc.stderr or proc.stdout[:300]
        raise RuntimeError(f"codex CLI error (rc={proc.returncode}): {err[:300]}")
    # codex stdout には進捗ログとモデル出力が混ざるので、最後の構造化ブロックを抽出
    return proc.stdout


def _claude_code(system: str, user: str) -> str:
    """Claude Code CLI 経由（サブスク内・API課金ゼロ）。
    ANTHROPIC_API_KEY を一時的に空にして API 課金モードを回避（残高ゼロ事故防止）。"""
    import subprocess
    import os
    prompt = f"{system}\n\n{user}"
    env = os.environ.copy()
    env["ANTHROPIC_API_KEY"] = ""    # サブスク経由に強制
    # 長文プロンプトは stdin パイプ経由で渡す（引数長制限回避）
    # timeout は codex(900s)と揃える。6/14 に 180s で timeout し chain が崩れた
    proc = subprocess.run(
        ["claude", "-p", "--output-format", "text"],
        input=prompt, env=env,
        capture_output=True, text=True,
        timeout=int(os.environ.get("CLAUDE_TEXT_TIMEOUT", "600")),
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

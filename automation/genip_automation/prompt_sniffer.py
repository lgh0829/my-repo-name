"""
prompt_sniffer.py — Task 2: 네트워크 인터셉트로 LLM 프롬프트 추출
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from playwright.sync_api import Page, Request

OUTPUT_JSON = Path(__file__).parent / "output" / "prompts.json"

# LLM API 호출로 추정되는 URL 패턴
LLM_URL_KEYWORDS = [
    "openai", "anthropic", "claude", "gpt",
    "api/chat", "api/generate", "api/completion", "api/llm",
    "generate", "completion", "chat/completions",
    "/v1/messages", "/v1/completions",
]

# 프롬프트가 포함될 가능성이 있는 필드명
PROMPT_FIELDS = ["prompt", "messages", "input", "query", "text", "content", "system"]

_captured: list[dict] = []


def _is_llm_request(url: str) -> bool:
    url_lower = url.lower()
    return any(kw in url_lower for kw in LLM_URL_KEYWORDS)


def _extract_prompt_from_body(body_str: str) -> Optional[dict]:
    """request body에서 프롬프트 관련 필드 추출."""
    try:
        data = json.loads(body_str)
    except (json.JSONDecodeError, ValueError):
        return None

    extracted = {}
    for field in PROMPT_FIELDS:
        if field in data:
            extracted[field] = data[field]

    # 중첩 구조 탐색 (e.g., {"body": {"messages": [...]}} )
    if not extracted:
        for key, val in data.items():
            if isinstance(val, dict):
                for field in PROMPT_FIELDS:
                    if field in val:
                        extracted[f"{key}.{field}"] = val[field]

    return extracted if extracted else None


def on_request(request: Request) -> None:
    """page.on('request') 핸들러 — LLM API 요청 감지 및 저장."""
    if request.method != "POST":
        return
    if not _is_llm_request(request.url):
        return

    try:
        body = request.post_data or ""
        prompt_data = _extract_prompt_from_body(body)

        entry = {
            "timestamp": datetime.now().isoformat(),
            "url": request.url,
            "method": request.method,
            "headers": dict(request.headers),
            "raw_body": body[:5000],  # 최대 5KB
            "extracted_prompts": prompt_data,
        }

        _captured.append(entry)
        print(f"[prompt_sniffer] LLM 요청 감지: {request.url}")
        if prompt_data:
            print(f"[prompt_sniffer]   추출된 필드: {list(prompt_data.keys())}")

        _save()

    except Exception as e:
        print(f"[prompt_sniffer] 요청 처리 오류: {e}")


def _save() -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(_captured, f, ensure_ascii=False, indent=2)


def attach(page: Page) -> None:
    """페이지에 네트워크 인터셉트 핸들러 등록."""
    page.on("request", on_request)
    print("[prompt_sniffer] 네트워크 인터셉트 활성화")


def get_captured() -> list[dict]:
    return list(_captured)


def print_summary() -> None:
    if not _captured:
        print("[prompt_sniffer] 감지된 LLM 요청 없음.")
        return

    print(f"\n[prompt_sniffer] 감지된 LLM 요청: {len(_captured)}건")
    for i, entry in enumerate(_captured, 1):
        print(f"  {i}. {entry['timestamp']} — {entry['url']}")
        if entry["extracted_prompts"]:
            for field, val in entry["extracted_prompts"].items():
                preview = str(val)[:200]
                print(f"     [{field}] {preview}")
    print(f"\n결과 파일: {OUTPUT_JSON}")

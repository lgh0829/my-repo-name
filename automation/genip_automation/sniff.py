"""
sniff.py — 브라우저를 열고 LLM API 요청을 자동 캡처
사용법: python3 sniff.py

1. 브라우저가 열리면 직접 로그인 후 기능 탐색
2. LLM 요청이 감지되면 터미널에 즉시 출력 + output/prompts.json 저장
3. 터미널에서 Ctrl+C로 종료
"""

import json
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, Request

OUTPUT = Path(__file__).parent / "output" / "prompts.json"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

LLM_PATTERNS = re.compile(
    r"openai|anthropic|/v1/chat|/v1/messages|/v1/completions|"
    r"api/chat|api/generate|api/llm|api/completion|bedrock|gemini",
    re.IGNORECASE,
)

captured: list[dict] = []


def handle_request(req: Request) -> None:
    if req.method != "POST":
        return
    if not LLM_PATTERNS.search(req.url):
        return

    body_str = req.post_data or ""
    try:
        body = json.loads(body_str)
    except Exception:
        body = body_str

    entry = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "url": req.url,
        "body": body,
    }
    captured.append(entry)

    # 터미널 즉시 출력
    print(f"\n{'='*60}")
    print(f"[{entry['time']}] LLM 요청 감지!")
    print(f"URL: {req.url}")
    if isinstance(body, dict):
        for key in ("messages", "prompt", "input", "system", "content"):
            if key in body:
                print(f"[{key}] {json.dumps(body[key], ensure_ascii=False)[:500]}")
    print(f"{'='*60}")

    # 파일 저장
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(captured, f, ensure_ascii=False, indent=2)


print("=" * 60)
print("1. Chrome을 종료하세요 (완전히)")
print("2. 아래 명령어로 Chrome을 디버그 모드로 재실행:")
print()
print("   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
print()
print("3. Chrome에서 genip.app 로그인 후 이 스크립트로 돌아오세요")
print("4. Enter를 누르면 연결을 시작합니다")
print("=" * 60)
input()

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]

    # 현재 열린 탭 중 genip.app 탭에 연결
    page = None
    for pg in context.pages:
        if "genip.app" in pg.url:
            page = pg
            break

    if page is None:
        page = context.pages[0]
        print(f"genip.app 탭을 못 찾아 첫 번째 탭에 연결: {page.url}")
    else:
        print(f"연결됨: {page.url}")

    page.on("request", handle_request)
    print(f"\nLLM 요청 모니터링 중... genip.app에서 기능을 사용하세요.")
    print(f"캡처 결과: {OUTPUT}")
    print("종료: Ctrl+C\n")

    try:
        input()
    except KeyboardInterrupt:
        pass
    finally:
        print(f"\n총 {len(captured)}건 캡처. 저장 위치: {OUTPUT}")

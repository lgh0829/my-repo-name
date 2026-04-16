"""
parse_har.py — Chrome DevTools HAR 파일에서 LLM 요청 추출

사용법:
  python3 parse_har.py <파일명.har>
  python3 parse_har.py  # output/ 폴더에서 최신 .har 파일 자동 탐색
"""

import json
import re
import sys
from pathlib import Path

OUTPUT = Path(__file__).parent / "output" / "prompts.json"

LLM_PATTERNS = re.compile(
    r"openai|anthropic|/v1/chat|/v1/messages|/v1/completions|"
    r"api/chat|api/generate|api/llm|api/completion|bedrock|"
    r"generativelanguage\.googleapis\.com|gemini",
    re.IGNORECASE,
)


def find_har_file() -> Path:
    candidates = sorted(Path(__file__).parent.glob("**/*.har"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        print("HAR 파일을 찾을 수 없습니다. 경로를 직접 인자로 전달하세요.")
        sys.exit(1)
    print(f"HAR 파일 자동 선택: {candidates[0]}")
    return candidates[0]


def extract_body(entry: dict):
    try:
        text = entry["request"]["postData"]["text"]
        return json.loads(text)
    except (KeyError, json.JSONDecodeError):
        try:
            return entry["request"]["postData"]["text"]
        except KeyError:
            return None


def parse(har_path: Path) -> list[dict]:
    with open(har_path, encoding="utf-8") as f:
        har = json.load(f)

    entries = har.get("log", {}).get("entries", [])
    results = []

    for entry in entries:
        url = entry.get("request", {}).get("url", "")
        if not LLM_PATTERNS.search(url):
            continue
        if entry.get("request", {}).get("method") != "POST":
            continue

        body = extract_body(entry)
        if body is None:
            continue

        result = {
            "url": url,
            "time": entry.get("startedDateTime", ""),
            "body": body,
        }
        results.append(result)

        # 터미널 출력
        print(f"\n{'='*60}")
        print(f"URL: {url}")
        if isinstance(body, dict):
            # Gemini 형식
            if "systemInstruction" in body:
                sys_text = body["systemInstruction"]["parts"][0]["text"]
                print(f"[system]\n{sys_text[:1000]}")
            if "contents" in body:
                for i, c in enumerate(body["contents"]):
                    role = c.get("role", "user")
                    text = c["parts"][0].get("text") or c["parts"][0].get("inlineData", {}).get("mimeType", "(binary)")
                    print(f"[{role} #{i+1}]\n{str(text)[:1000]}")
            # OpenAI 형식
            for key in ("messages", "prompt", "input"):
                if key in body:
                    print(f"[{key}] {json.dumps(body[key], ensure_ascii=False)[:800]}")
        print(f"{'='*60}")

    return results


har_path = Path(sys.argv[1]) if len(sys.argv) > 1 else find_har_file()
results = parse(har_path)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n총 {len(results)}건 추출 → {OUTPUT}")

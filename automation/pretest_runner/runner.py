#!/usr/bin/env python3
"""PatSol Prompt Monitor 자동화 테스트 러너

사용법:
  # 의존성 설치 (최초 1회)
  uv sync
  uv run playwright install chromium

  # 전체 실행 (헤드리스)
  uv run python runner.py

  # TC 그룹만, 브라우저 표시
  uv run python runner.py --group TC --headful

  # 특정 케이스만 (느린 속도로 디버그)
  uv run python runner.py --cases TC-01 AM-06 --headful --slow-mo 800

  # 결과 저장 경로 지정
  uv run python runner.py --group BK --out results/bk_test.csv
"""

import asyncio
import json
import csv
import argparse
import re
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright, Page, TimeoutError as PWTimeout

BASE_URL = "https://d2mzt9js79l2iz.cloudfront.net/pretest"
RESULTS_DIR = Path(__file__).parent / "results"

# ─── DOM 셀렉터 ───────────────────────────────────────────────────────────────
# 실제 DOM 구조와 맞지 않으면 --headful 모드로 열어 개발자 도구로 확인 후 수정하세요.

# 에이전트 탭 (Orchestrator / Review / Author)
SEL_AGENT_TAB    = "button:has-text('Orchestrator'), [role='tab']:has-text('Orchestrator')"

# 메시지 입력창 (화면 상단 textarea)
SEL_MESSAGE      = "textarea"

# 컨텍스트 탭 (청구항 / 발명의설명 / 도면)
SEL_CTX_TAB      = "button:has-text('{name}'), [role='tab']:has-text('{name}')"

# 실행 버튼
SEL_RUN          = "button:has-text('실행')"

# 결과 출력 영역 (JSON이 표시되는 pre/code/div)
SEL_RESULT       = "pre, code, [class*='output'], [class*='result'], [data-testid*='result']"

# 평가 버튼
SEL_THUMB_UP     = "button:has-text('👍')"
SEL_THUMB_DOWN   = "button:has-text('👎')"
SEL_LABEL        = "button:has-text('{label}')"

# 메모 + 저장
SEL_MEMO         = "textarea[placeholder*='메모'], [data-testid*='memo'] textarea, .memo textarea"
SEL_SAVE         = "button:has-text('평가 저장')"
# ──────────────────────────────────────────────────────────────────────────────

REQUIRED_FIELDS = {"intent", "confidence"}


def auto_evaluate(
    parsed: dict,
    expected_intent: str | None,
    match_type: str = "exact",
) -> tuple[str | None, str | None]:
    """(thumb, label) 반환.

    label: 정확 | 부정확 | 형식오류 | 근거부족 | None(수동 필요)
    """
    if not REQUIRED_FIELDS.issubset(parsed.keys()):
        return "👎", "형식오류"

    actual = str(parsed.get("intent", ""))
    conf   = float(parsed.get("confidence", 0))

    if expected_intent is None:
        return None, None

    hit = {
        "exact":      actual == expected_intent,
        "contains":   expected_intent in actual,
        "startswith": actual.startswith(expected_intent),
    }.get(match_type, actual == expected_intent)

    if hit:
        return "👍", "정확"
    return ("👎", "근거부족") if conf >= 0.8 else ("👎", "부정확")


async def _try_click(page: Page, selector: str, timeout: int = 3000) -> bool:
    try:
        await page.click(selector, timeout=timeout)
        return True
    except PWTimeout:
        return False


async def _fill_contexts(page: Page, context_spec: str, sample: dict):
    """context_spec 예: '청구항', '청구항+발명의설명'"""
    tab_key = {"청구항": "claims", "발명의설명": "spec", "도면": "drawings"}
    for tab in context_spec.split("+"):
        tab = tab.strip()
        key = tab_key.get(tab)
        content = sample.get(key) if key else None
        if not content:
            continue

        sel = SEL_CTX_TAB.format(name=tab)
        if not await _try_click(page, sel):
            print(f"  [warn] 컨텍스트 탭 '{tab}' 없음 — 건너뜀")
            continue
        await page.wait_for_timeout(400)

        # 화면에 보이는 textarea 중 메시지 입력창을 제외한 마지막 것을 대상으로 함
        textareas = await page.locator("textarea:visible").all()
        target = textareas[-1] if len(textareas) >= 2 else (textareas[0] if textareas else None)
        if target is None:
            print(f"  [warn] 컨텍스트 textarea 없음 ({tab})")
            continue
        await target.fill(content)


async def run_one(page: Page, tc: dict, samples: dict, delay_ms: int) -> dict:
    rec = {
        "id":               tc["id"],
        "taxonomy":         tc["taxonomy"],
        "message":          tc["message"],
        "expected_intent":  tc.get("expected_intent"),
        "timestamp":        datetime.now().isoformat(),
        "raw_output":       None,
        "parsed_intent":    None,
        "parsed_confidence":None,
        "thumb":            None,
        "auto_label":       None,
        "memo":             "",
        "error":            None,
    }
    print(f"\n[{tc['id']}] {tc['message'][:70]}")

    try:
        # 페이지 새로 로드 (테스트 간 상태 초기화)
        await page.goto(BASE_URL, wait_until="networkidle", timeout=20000)

        # Orchestrator 탭 선택
        await _try_click(page, SEL_AGENT_TAB)
        await page.wait_for_timeout(300)

        # 메시지 입력 (첫 번째 textarea)
        msg = page.locator(SEL_MESSAGE).first
        await msg.click()
        await msg.fill(tc["message"])

        # 컨텍스트 채우기
        sample_key   = tc.get("sample_data") or ""
        context_spec = tc.get("context") or ""
        sample_data  = samples.get(sample_key, {})
        if context_spec and sample_data:
            await _fill_contexts(page, context_spec, sample_data)

        # 실행
        await page.click(SEL_RUN, timeout=5000)

        # 결과 대기 (최대 45초)
        result_loc = page.locator(SEL_RESULT)
        await result_loc.first.wait_for(state="visible", timeout=45000)
        await page.wait_for_timeout(600)

        # intent 필드가 포함된 블록 찾기
        raw = ""
        for loc in await result_loc.all():
            text = await loc.inner_text()
            if "intent" in text and "{" in text:
                raw = text
                break
        if not raw:
            raw = await result_loc.first.inner_text()
        rec["raw_output"] = raw

        # JSON 추출
        m = re.search(r"\{[^{}]*\"intent\"\s*:[^{}]*\}", raw, re.DOTALL)
        if not m:
            rec["error"] = "no_intent_json"
            print(f"  [error] JSON에서 intent 필드를 찾지 못했습니다.")
            return rec

        parsed = json.loads(m.group())
        rec["parsed_intent"]     = parsed.get("intent")
        rec["parsed_confidence"] = parsed.get("confidence")

        # 자동 평가
        thumb, label = auto_evaluate(parsed, tc.get("expected_intent"), tc.get("match_type", "exact"))
        rec["thumb"]      = thumb
        rec["auto_label"] = label
        tag = f"{thumb} {label}" if thumb else "수동 검토 필요"
        print(f"  → intent={rec['parsed_intent']} conf={rec['parsed_confidence']} | {tag}")

        # UI에 평가 반영
        if thumb:
            sel = SEL_THUMB_UP if thumb == "👍" else SEL_THUMB_DOWN
            if not await _try_click(page, sel):
                print(f"  [warn] {thumb} 버튼 없음")
            await page.wait_for_timeout(300)

        if label:
            if not await _try_click(page, SEL_LABEL.format(label=label)):
                print(f"  [warn] '{label}' 버튼 없음")
            await page.wait_for_timeout(300)

        # 메모
        memo_text = label or "manual_review_needed"
        rec["memo"] = memo_text
        memo_loc = page.locator(SEL_MEMO)
        if await memo_loc.count() > 0:
            try:
                if await memo_loc.first.is_visible(timeout=1500):
                    await memo_loc.first.fill(memo_text)
            except PWTimeout:
                pass

        # 저장
        if not await _try_click(page, SEL_SAVE):
            print(f"  [warn] '평가 저장' 버튼 없음")
        await page.wait_for_timeout(delay_ms)

    except Exception as e:
        rec["error"] = str(e)
        print(f"  [error] {e}")

    return rec


def write_csv(records: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "id", "taxonomy", "message", "expected_intent", "timestamp",
        "parsed_intent", "parsed_confidence", "thumb", "auto_label",
        "memo", "error", "raw_output",
    ]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(records)
    print(f"\n✓ 결과 저장: {path}")


async def main():
    parser = argparse.ArgumentParser(description="PatSol Prompt Monitor 자동화 러너")
    parser.add_argument("--headful",  action="store_true", help="브라우저 창 표시")
    parser.add_argument("--slow-mo",  type=int, default=0,    metavar="MS", help="동작 딜레이(ms) — 디버그용")
    parser.add_argument("--delay",    type=int, default=1500, metavar="MS", help="테스트 완료 후 대기(ms)")
    parser.add_argument("--cases",    nargs="+", metavar="ID",              help="실행할 케이스 (예: TC-01 AM-06)")
    parser.add_argument("--group",    choices=["TC", "AM", "BK", "all"], default="all")
    parser.add_argument("--out",      metavar="FILE",                        help="결과 CSV 경로")
    args = parser.parse_args()

    base = Path(__file__).parent
    with open(base / "test_cases.json", encoding="utf-8") as f:
        all_cases: list[dict] = json.load(f)
    with open(base / "sample_data.json", encoding="utf-8") as f:
        samples: dict = json.load(f)

    if args.cases:
        cases = [c for c in all_cases if c["id"] in args.cases]
    elif args.group != "all":
        cases = [c for c in all_cases if c["id"].startswith(args.group)]
    else:
        cases = all_cases

    if not cases:
        print("실행할 테스트 케이스가 없습니다.")
        return

    print(f"테스트 {len(cases)}건 실행 (URL: {BASE_URL})")
    out_path = Path(args.out) if args.out else (
        RESULTS_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    records: list[dict] = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=not args.headful, slow_mo=args.slow_mo)
        page = await browser.new_page()

        for tc in cases:
            rec = await run_one(page, tc, samples, args.delay)
            records.append(rec)

        await browser.close()

    write_csv(records, out_path)

    correct  = sum(1 for r in records if r["auto_label"] == "정확")
    schema_e = sum(1 for r in records if r["auto_label"] == "형식오류")
    manual   = sum(1 for r in records if r["thumb"] is None and not r["error"])
    errors   = sum(1 for r in records if r["error"])

    print("\n── 결과 요약 ──────────────────")
    print(f"전체:         {len(records)}건")
    print(f"정확:         {correct}건")
    print(f"형식오류:     {schema_e}건")
    print(f"수동 검토:    {manual}건")
    print(f"실행 오류:    {errors}건")


if __name__ == "__main__":
    asyncio.run(main())

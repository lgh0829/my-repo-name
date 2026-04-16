"""
score_evaluator.py
클라우드바우처 이용계획서 자동 채점·갭분석기 (Claude API 기반)

사용법:
    python3 score_evaluator.py --company 특허법인_공간
    python3 score_evaluator.py --company 특허법인_공간 --templates T01,T03
    python3 score_evaluator.py --draft outputs/특허법인_공간/draft_T01.md

입력:
    - outputs/{company_name}/draft_T*.md  (draft_generator.py 출력물)

출력:
    - outputs/{company_name}/evaluation_report.md  (전체 비교 리포트)
    - outputs/{company_name}/eval_T*.md             (템플릿별 상세 평가)
"""

import asyncio
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import anthropic

# ─────────────────────────────────────────────
# 경로 설정
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
OUTPUTS_DIR = BASE_DIR / "outputs"

# ─────────────────────────────────────────────
# 평가 기준 정의
# ─────────────────────────────────────────────
EVAL_CRITERIA = [
    {
        "id": "C1",
        "name": "지원 필요성",
        "max_score": 20,
        "tiebreak_priority": 3,
        "sub_criteria": [
            {"id": "C1a", "name": "기업의 클라우드 도입·이용 역량", "max_score": 10},
            {"id": "C1b", "name": "도입 및 정부지원 필요성", "max_score": 10},
        ],
        "description": (
            "기업이 클라우드를 도입·활용할 역량이 있는지, "
            "정부 지원 없이는 자체 도입이 어렵다는 논거가 충분한지 평가"
        ),
    },
    {
        "id": "C2",
        "name": "서비스 이용 계획의 적절성",
        "max_score": 30,
        "tiebreak_priority": 2,
        "sub_criteria": [
            {"id": "C2a", "name": "업무환경 개선 의지", "max_score": 10},
            {"id": "C2b", "name": "서비스 구성 적절성·예산 활용성", "max_score": 10},
            {"id": "C2c", "name": "이용계획 구체성·적절성", "max_score": 10},
        ],
        "description": (
            "PatSol 서비스를 실제 업무에 어떻게 활용할지 구체적이고 적절하게 서술했는지, "
            "예산 규모 대비 활용 계획이 합리적인지 평가"
        ),
    },
    {
        "id": "C3",
        "name": "디지털 전환 및 선도사례 가능성",
        "max_score": 30,
        "tiebreak_priority": 1,
        "is_tiebreak_top": True,
        "sub_criteria": [
            {"id": "C3a", "name": "디지털 전환 가능성·적절성", "max_score": 10},
            {"id": "C3b", "name": "산업 내 선도사례 가능성", "max_score": 10},
            {"id": "C3c", "name": "AI 접목 서비스 및 산업도메인 특화 서비스 활용도", "max_score": 10},
        ],
        "description": (
            "특허 분야 디지털 전환 가능성과 업계 선도사례 창출 가능성, "
            "특히 AI 접목 및 IP 도메인 특화 활용도가 명시적으로 서술되었는지 평가 (동점 시 최우선 기준)"
        ),
    },
    {
        "id": "C4",
        "name": "기대효과",
        "max_score": 20,
        "tiebreak_priority": 4,
        "sub_criteria": [
            {"id": "C4a", "name": "매출 증대·업무 효율성 향상", "max_score": 10},
            {"id": "C4b", "name": "서비스 이용 촉진 파급 효과", "max_score": 10},
        ],
        "description": (
            "PatSol 도입으로 인한 구체적 효과 (수치 근거 포함 여부, "
            "업계 파급 효과 서술 여부) 평가"
        ),
    },
]

TOTAL_MAX = sum(c["max_score"] for c in EVAL_CRITERIA)


# ─────────────────────────────────────────────
# 단일 초안 평가 프롬프트 생성
# ─────────────────────────────────────────────
def build_eval_system_prompt() -> str:
    return """당신은 정부 지원사업(클라우드 서비스 보급·확산 사업) 선정 평가위원입니다.
제출된 수요기업 이용계획서를 아래 기준에 따라 채점하고, 항목별 갭과 개선 방향을 제시합니다.

[평가 원칙]
- 각 소항목은 10점 만점으로 독립 채점 (정수 단위)
- 점수 근거를 구체적 문장 인용과 함께 제시
- 부족한 논거가 있으면 개선 방향을 1~2문장으로 명시
- ❸항목(AI 접목·도메인 특화)은 동점 시 최우선 기준이므로 엄격하게 채점"""


def build_eval_user_prompt(draft_content: str, template_meta: str) -> str:
    criteria_text = []
    for c in EVAL_CRITERIA:
        sub_text = "\n".join(
            f"    - {s['id']} {s['name']} (10점)" for s in c["sub_criteria"]
        )
        tiebreak = " ★동점시최우선★" if c.get("is_tiebreak_top") else f" (동점시우선순위 {c['tiebreak_priority']})"
        criteria_text.append(
            f"  ❶~❹ 중 {c['id']} [{c['name']}] 최대 {c['max_score']}점{tiebreak}\n"
            f"  {c['description']}\n"
            f"  소항목:\n{sub_text}"
        )

    criteria_block = "\n\n".join(criteria_text)

    return f"""아래 이용계획서 초안을 평가해주세요.

## 초안 메타정보
{template_meta}

## 이용계획서 초안
{draft_content}

---

## 평가 기준
{criteria_block}

---

## 출력 형식 (반드시 준수)

다음 JSON 형식으로만 응답하세요. 다른 텍스트 없이 JSON만 출력하세요.

```json
{{
  "template_id": "T00",
  "scores": {{
    "C1a": 0, "C1b": 0,
    "C2a": 0, "C2b": 0, "C2c": 0,
    "C3a": 0, "C3b": 0, "C3c": 0,
    "C4a": 0, "C4b": 0
  }},
  "evidence": {{
    "C1a": "점수 근거 (해당 문장 인용 또는 '해당 내용 없음')",
    "C1b": "점수 근거",
    "C2a": "점수 근거",
    "C2b": "점수 근거",
    "C2c": "점수 근거",
    "C3a": "점수 근거",
    "C3b": "점수 근거",
    "C3c": "점수 근거",
    "C4a": "점수 근거",
    "C4b": "점수 근거"
  }},
  "gaps": {{
    "C1a": "개선 방향 (충분하면 null)",
    "C1b": "개선 방향",
    "C2a": "개선 방향",
    "C2b": "개선 방향",
    "C2c": "개선 방향",
    "C3a": "개선 방향",
    "C3b": "개선 방향",
    "C3c": "개선 방향",
    "C4a": "개선 방향",
    "C4b": "개선 방향"
  }},
  "strengths": ["강점 1", "강점 2"],
  "overall_comment": "전체 한줄 총평"
}}
```"""


# ─────────────────────────────────────────────
# 단일 초안 평가
# ─────────────────────────────────────────────
async def evaluate_draft(
    client: anthropic.AsyncAnthropic,
    draft_path: Path,
) -> dict:
    """단일 초안 평가 → 점수 dict 반환"""
    draft_content = draft_path.read_text(encoding="utf-8")

    # 메타정보 추출 (파일 상단 2~3줄)
    meta_lines = [l for l in draft_content.split("\n")[:5] if l.strip()]
    template_meta = "\n".join(meta_lines)

    system_prompt = build_eval_system_prompt()
    user_prompt = build_eval_user_prompt(draft_content, template_meta)

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt,
    )

    raw = message.content[0].text.strip()

    # JSON 추출 (```json ... ``` 블록 또는 raw JSON)
    json_match = re.search(r"```json\s*([\s\S]+?)\s*```", raw)
    if json_match:
        raw = json_match.group(1)

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # 파싱 실패 시 기본 구조 반환
        result = {
            "template_id": draft_path.stem.replace("draft_", ""),
            "scores": {},
            "evidence": {},
            "gaps": {},
            "strengths": [],
            "overall_comment": f"[파싱 오류] 원본: {raw[:200]}",
            "_parse_error": True,
        }

    result["_draft_path"] = str(draft_path)
    return result


# ─────────────────────────────────────────────
# 점수 집계
# ─────────────────────────────────────────────
def compute_totals(result: dict) -> dict:
    """소항목 점수 → 항목별 합계 + 총점 계산"""
    scores = result.get("scores", {})
    totals = {}
    grand_total = 0

    for c in EVAL_CRITERIA:
        sub_total = sum(scores.get(s["id"], 0) for s in c["sub_criteria"])
        totals[c["id"]] = sub_total
        grand_total += sub_total

    totals["TOTAL"] = grand_total
    return totals


# ─────────────────────────────────────────────
# 마크다운 리포트 생성
# ─────────────────────────────────────────────
def build_comparison_report(results: list[dict], company_name: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 클라우드바우처 이용계획서 평가 리포트",
        f"> 기업: {company_name} | 평가일: {now}",
        "",
        "## 1. 점수 비교표",
        "",
    ]

    # 헤더
    header_ids = [""] + [r.get("template_id", "?") for r in results]
    lines.append("| 항목 | " + " | ".join(header_ids[1:]) + " |")
    lines.append("|" + "---|" * (len(results) + 1))

    # 항목별 행
    for c in EVAL_CRITERIA:
        tiebreak_mark = " ★" if c.get("is_tiebreak_top") else ""
        row = [f"❶~❹ {c['id']} {c['name']}{tiebreak_mark} (/{c['max_score']})"]
        for r in results:
            totals = compute_totals(r)
            row.append(str(totals.get(c["id"], "-")))
        lines.append("| " + " | ".join(row) + " |")

        # 소항목 행
        for s in c["sub_criteria"]:
            sub_row = [f"　 {s['id']} {s['name']} (/10)"]
            for r in results:
                sub_row.append(str(r.get("scores", {}).get(s["id"], "-")))
            lines.append("| " + " | ".join(sub_row) + " |")

    # 총점 행
    total_row = ["**총점 (/100)**"]
    for r in results:
        totals = compute_totals(r)
        total_row.append(f"**{totals.get('TOTAL', '-')}**")
    lines.append("| " + " | ".join(total_row) + " |")

    lines += ["", "---", ""]

    # 2. 순위 요약
    lines.append("## 2. 순위 요약")
    lines.append("")

    scored = []
    for r in results:
        totals = compute_totals(r)
        scored.append({
            "id": r.get("template_id", "?"),
            "total": totals.get("TOTAL", 0),
            "C3": totals.get("C3", 0),
            "comment": r.get("overall_comment", ""),
        })

    # 총점 → C3 점수 순으로 정렬
    scored.sort(key=lambda x: (x["total"], x["C3"]), reverse=True)

    lines.append("| 순위 | 템플릿 | 총점 | ❸ AI·특화(★) | 총평 |")
    lines.append("|---|---|---|---|---|")
    for rank, s in enumerate(scored, 1):
        lines.append(
            f"| {rank} | {s['id']} | {s['total']} | {s['C3']} | {s['comment']} |"
        )

    lines += ["", "---", ""]

    # 3. 템플릿별 갭 분석
    lines.append("## 3. 템플릿별 갭 분석")
    lines.append("")

    for r in results:
        tid = r.get("template_id", "?")
        totals = compute_totals(r)
        lines.append(f"### {tid} (총점: {totals.get('TOTAL', '-')}/100)")
        lines.append("")

        # 강점
        strengths = r.get("strengths", [])
        if strengths:
            lines.append("**강점**")
            for s in strengths:
                lines.append(f"- {s}")
            lines.append("")

        # 갭 (null이 아닌 항목만)
        gaps = r.get("gaps", {})
        gap_items = [(k, v) for k, v in gaps.items() if v]
        if gap_items:
            lines.append("**개선 필요 항목**")
            for k, v in gap_items:
                score = r.get("scores", {}).get(k, "?")
                lines.append(f"- **{k}** ({score}/10): {v}")
            lines.append("")
        else:
            lines.append("*갭 없음*")
            lines.append("")

    lines += ["---", ""]
    lines.append(f"*생성: {now} | score_evaluator.py*")

    return "\n".join(lines)


def build_detail_report(result: dict) -> str:
    """템플릿별 상세 평가 리포트"""
    tid = result.get("template_id", "?")
    totals = compute_totals(result)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# {tid} 상세 평가 리포트",
        f"> 총점: {totals.get('TOTAL', '-')}/100 | 평가일: {now}",
        "",
    ]

    for c in EVAL_CRITERIA:
        tiebreak_mark = " ★(동점시최우선)" if c.get("is_tiebreak_top") else ""
        c_total = totals.get(c["id"], 0)
        lines.append(f"## {c['id']} {c['name']}{tiebreak_mark} — {c_total}/{c['max_score']}점")
        lines.append("")

        for s in c["sub_criteria"]:
            score = result.get("scores", {}).get(s["id"], 0)
            evidence = result.get("evidence", {}).get(s["id"], "")
            gap = result.get("gaps", {}).get(s["id"], None)

            lines.append(f"### {s['id']} {s['name']} — {score}/10")
            if evidence:
                lines.append(f"**근거**: {evidence}")
            if gap:
                lines.append(f"**개선 방향**: {gap}")
            lines.append("")

    comment = result.get("overall_comment", "")
    if comment:
        lines.append(f"---\n\n**총평**: {comment}")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# 출력 저장
# ─────────────────────────────────────────────
def save_report(content: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ─────────────────────────────────────────────
# 메인 실행
# ─────────────────────────────────────────────
async def main(company_name: str | None, template_ids: list[str] | None, single_draft: str | None):
    client = anthropic.AsyncAnthropic()

    # 평가 대상 파일 수집
    if single_draft:
        draft_paths = [Path(single_draft)]
        company_name = Path(single_draft).parent.name
    else:
        company_dir = OUTPUTS_DIR / company_name
        if not company_dir.exists():
            print(f"[오류] 디렉토리 없음: {company_dir}")
            return

        all_drafts = sorted(company_dir.glob("draft_T*.md"))
        if template_ids:
            draft_paths = [p for p in all_drafts if any(tid in p.stem for tid in template_ids)]
        else:
            draft_paths = all_drafts

    if not draft_paths:
        print("[오류] 평가할 초안 파일이 없습니다.")
        return

    print(f"[{company_name}] 평가 시작 — {len(draft_paths)}개 초안")

    # 병렬 평가
    tasks = [evaluate_draft(client, p) for p in draft_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 오류 필터링
    valid_results = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            print(f"  [오류] {draft_paths[i].name}: {r}")
        else:
            tid = r.get("template_id", draft_paths[i].stem)
            totals = compute_totals(r)
            print(f"  [{tid}] 총점: {totals.get('TOTAL', '-')}/100")
            valid_results.append(r)

    if not valid_results:
        print("[오류] 유효한 평가 결과 없음")
        return

    # 리포트 저장
    out_dir = OUTPUTS_DIR / company_name

    # 비교 리포트
    comparison = build_comparison_report(valid_results, company_name)
    report_path = out_dir / "evaluation_report.md"
    save_report(comparison, report_path)
    print(f"\n비교 리포트 저장: {report_path}")

    # 템플릿별 상세 리포트
    for r in valid_results:
        tid = r.get("template_id", "unknown")
        detail = build_detail_report(r)
        detail_path = out_dir / f"eval_{tid}.md"
        save_report(detail, detail_path)

    print(f"상세 평가 저장: {out_dir}/eval_T*.md")
    print("\n완료.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="클라우드바우처 이용계획서 자동 채점기")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--company", help="기업명 (outputs/{company}/draft_T*.md 일괄 평가)")
    group.add_argument("--draft", help="단일 초안 파일 경로")
    parser.add_argument(
        "--templates",
        default=None,
        help="평가할 템플릿 ID (쉼표 구분, 예: T01,T03). 미지정 시 전체",
    )
    args = parser.parse_args()

    template_ids = [t.strip() for t in args.templates.split(",")] if args.templates else None

    asyncio.run(main(args.company, template_ids, args.draft))

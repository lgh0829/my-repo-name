"""
draft_generator.py
클라우드바우처 이용계획서 자동 초안 생성기 (Claude API 기반)

사용법:
    python draft_generator.py --survey survey_gonggan.json [--templates T01,T03] [--output-dir outputs]

입력:
    - survey JSON: survey_schema.json 형식에 맞는 기업 설문 데이터
    - template JSON: templates/template_*.json (기본: 전체 10종)
    - base_content.md: 핵심 논거 풀

출력:
    - outputs/{company_name}/draft_T01.md ~ draft_T10.md
"""

import asyncio
import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path

import anthropic

# ─────────────────────────────────────────────
# 경로 설정
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUTS_DIR = BASE_DIR / "outputs"
BASE_CONTENT_PATH = BASE_DIR / "base_content.md"


# ─────────────────────────────────────────────
# 설문 데이터 로드
# ─────────────────────────────────────────────
def load_survey(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────
# 템플릿 로드
# ─────────────────────────────────────────────
def load_templates(template_ids: list[str] | None = None) -> list[dict]:
    templates = []
    for path in sorted(TEMPLATES_DIR.glob("template_*.json")):
        with open(path, encoding="utf-8") as f:
            tpl = json.load(f)
        if template_ids is None or tpl["id"] in template_ids:
            templates.append(tpl)
    return templates


# ─────────────────────────────────────────────
# base_content.md 로드
# ─────────────────────────────────────────────
def load_base_content() -> str:
    with open(BASE_CONTENT_PATH, encoding="utf-8") as f:
        return f.read()


# ─────────────────────────────────────────────
# 설문 데이터 → 자연어 요약 (프롬프트 주입용)
# ─────────────────────────────────────────────
def survey_to_text(s: dict) -> str:
    pain_map = {
        "수작업_많음": "수작업이 많음",
        "시스템_분산": "시스템 분산",
        "보안_우려": "보안 우려",
        "인력_부족": "인력 부족",
        "비용_부담": "비용 부담",
    }
    goal_map = {
        "업무_효율화": "업무 효율화",
        "보안_강화": "보안 강화",
        "비용_절감": "비용 절감",
        "경쟁력_강화": "경쟁력 강화",
        "성장_잠재력": "성장 잠재력 확보",
    }
    cloud_state_map = {
        "현재_미사용": "현재 클라우드 미사용",
        "일부_사용중": "일부 업무에 클라우드 사용 중",
        "주요업무에_사용중": "주요 업무에 클라우드 사용 중",
    }
    it_staff_map = {
        "없음": "IT 전담 인력 없음",
        "1명": "IT 담당 1명",
        "2~3명": "IT 담당 2~3명",
        "4명이상": "IT 담당 4명 이상",
    }
    data_mgmt_map = {
        "개인PC": "개인 PC 중심 데이터 관리",
        "사내서버": "사내 서버 보유",
        "외부클라우드": "외부 클라우드 일부 활용",
        "혼용": "개인 PC + 서버 혼용",
    }
    it_scale_map = {
        "소형_PC복합기중심": "소형 IT 자산 (PC·복합기 중심)",
        "중형_사내서버보유": "중형 IT 자산 (사내 서버 보유)",
        "대형_전용인프라운영": "대형 IT 자산 (전용 인프라 운영)",
    }
    readiness_map = {
        "도입_검토전": "클라우드 도입 검토 전 단계",
        "도입_검토중": "클라우드 도입 검토 중",
        "도입_결정완료": "클라우드 도입 결정 완료",
    }

    pain = s.get("pain_points_rank", {})
    goal = s.get("goal_rank", {})
    total_emp = s.get("employees_patent", 0) + s.get("employees_non_patent", 0)

    lines = [
        f"[기업 정보]",
        f"- 기업명: {s.get('company_name', '')}",
        f"- 주요 업무: {s.get('main_work', '')}",
        f"- 강점: {s.get('strengths', '')}",
        f"- 임직원: 총 {total_emp}명 (변리사·보조 {s.get('employees_patent', 0)}명, 비변리 {s.get('employees_non_patent', 0)}명)",
        "",
        f"[도입 목적 및 문제점]",
        f"- 문제점 1순위: {pain_map.get(pain.get('first', ''), pain.get('first', ''))}",
        f"- 문제점 2순위: {pain_map.get(pain.get('second', ''), pain.get('second', ''))}",
        f"- 목표 1순위: {goal_map.get(goal.get('first', ''), goal.get('first', ''))}",
        f"- 목표 2순위: {goal_map.get(goal.get('second', ''), goal.get('second', ''))}",
        "",
        f"[클라우드 현황]",
        f"- 현재 클라우드 사용: {cloud_state_map.get(s.get('cloud_current_state', ''), s.get('cloud_current_state', ''))}",
        f"- 전환 준비도: {readiness_map.get(s.get('cloud_readiness', ''), s.get('cloud_readiness', ''))}",
        f"- IT 인력: {it_staff_map.get(s.get('it_staff', ''), s.get('it_staff', ''))}",
        f"- 데이터 관리: {data_mgmt_map.get(s.get('data_management', ''), s.get('data_management', ''))}",
        f"- IT 자산 규모: {it_scale_map.get(s.get('it_asset_scale', ''), s.get('it_asset_scale', ''))}",
        f"- 도입 방식: {s.get('cloud_method', '').replace('_', ' ')}",
        f"- 도입 시기: {s.get('cloud_timeline', '').replace('_', ' ')}",
    ]

    # 선택 항목
    optionals = []
    if s.get("key_customers"):
        optionals.append(f"- 주요 고객: {s['key_customers'].replace('_', ' ')}")
    if s.get("cloud_budget"):
        optionals.append(f"- 클라우드 예산: {s['cloud_budget'].replace('_', ' ')}")
    if s.get("revenue_scale"):
        optionals.append(f"- 매출 규모: {s['revenue_scale']}")
    if s.get("current_tools"):
        optionals.append(f"- 현재 사용 툴: {s['current_tools']}")
    if s.get("specific_concerns"):
        optionals.append(f"- 기타 우려사항: {s['specific_concerns']}")

    if optionals:
        lines.append("")
        lines.append("[선택 정보]")
        lines.extend(optionals)

    return "\n".join(lines)


# ─────────────────────────────────────────────
# SYSTEM PROMPT 생성
# ─────────────────────────────────────────────
def build_system_prompt() -> str:
    return """당신은 정부 지원사업 신청서 작성 전문가입니다. 중소기업의 클라우드 서비스 도입 이용계획서를 작성합니다.

[도메인 컨텍스트]
- 대상 문서: 클라우드 서비스 보급·확산 사업 수요기업 이용계획서
- 공급 서비스: PatSol (주식회사 완드) — 특허 선행기술조사·청구항 설계·명세서 작성 지원 B2B SaaS
- 평가자: 정부 선정 평가위원
- 평가 배점: ❶지원필요성(20) ❷이용계획적절성(30) ❸디지털전환·선도사례(30, 최우선) ❹기대효과(20)

[PatSol 핵심 기능]
1. 국내외 특허 DB 통합 검색 (KIPRIS·USPTO)
2. 유사도 기반 벡터 검색 + 자연어 검색 병행
3. OS(Object & Solution) 매트릭스 비교발명 분석 / 공백기술 탐색
4. 선행기술조사-청구항 설계 연계 (직결 연동)
5. 명세서 초안 작성 보조 (기재불비 위험 저감)
6. 사건 이력 중앙집중형 관리 + Public 클라우드 환경에서 데이터 보안

[서술 규칙]
- 본문 계층: 1, 가, 1), ㅇ, -, · 순서 준수
- 단순 도입 의지가 아닌 현황 기반의 구체적 필요성 중심 서술
- 수치·근거를 동반한 서술 선호 (출처 없는 단순 수치라도 현실적 범위 내 사용 가능)
- 허위 내용 작성 금지

[❸ 우대 항목 필수 포함 요소]
모든 초안에 아래 요소를 반드시 포함할 것:
- "유사도 기반 벡터 검색" 또는 "AI 기반 유사도 검색" 표현
- "특허 도메인에 특화된" 또는 "IP 특화" 표현
- "AI 초안 보조 → 변리사 최종 확정" 협업 구조 언급"""


# ─────────────────────────────────────────────
# USER PROMPT 생성 (섹션별 분할 생성)
# ─────────────────────────────────────────────
def build_user_prompt(survey_text: str, template: dict, base_content: str, section: str) -> str:
    """섹션별 프롬프트 생성"""

    # 섹션별 base_content 추출
    section_content_map = {
        "ga": ["섹션 A", "섹션 B", "섹션 C", "섹션 D"],
        "na": ["섹션 E"],
        "da": ["섹션 F"],
        "ma": ["섹션 G"],
    }
    target_sections = section_content_map.get(section, [])
    relevant_content = extract_base_content_sections(base_content, target_sections)

    # 템플릿 지시사항 구성
    tpl_instruction = build_template_instruction(template, section)

    return f"""아래 기업 정보와 템플릿 지시사항을 바탕으로 클라우드바우처 이용계획서의 해당 섹션을 작성해주세요.

## 기업 설문 정보
{survey_text}

## 핵심 논거 풀 (참고용 — 그대로 옮기지 말고 변형하여 활용)
{relevant_content}

## 템플릿 지시사항
{tpl_instruction}

## 출력 형식
- 계층 구조 준수: ㅇ (대항목) → - (세부 항목)
- 각 ㅇ 항목: 제목 없이 첫 문장부터 시작 (제목을 ㅇ 앞에 따로 붙이지 않음)
- 전문적이고 간결한 어조
- 마크다운 헤더(#, ##) 사용 금지
"""


def extract_base_content_sections(base_content: str, section_keys: list[str]) -> str:
    """base_content.md에서 특정 섹션만 추출"""
    if not section_keys:
        return base_content

    lines = base_content.split("\n")
    result = []
    in_target = False
    current_section = ""

    for line in lines:
        # 섹션 헤더 감지 (## [섹션 X] ...)
        match = re.match(r"^## \[(섹션 [A-Z])\]", line)
        if match:
            current_section = match.group(1)
            in_target = any(key in current_section for key in section_keys)

        if in_target:
            result.append(line)

    return "\n".join(result) if result else base_content[:2000]


def build_template_instruction(template: dict, section: str) -> str:
    """템플릿 JSON → 섹션별 지시사항 텍스트 변환"""
    lines = [
        f"템플릿 ID: {template['id']} — {template['name']}",
        f"강조점: {template['emphasis']}",
        f"서술 방식: {template['style']}",
        f"논거 프레임: {template['frame']}",
        "",
    ]

    wi = template.get("writing_instructions", {})

    if section == "ga":
        lines.append(f"[가. 이용목적 섹션 구성] — {template.get('structure_ga', '')} 구조")
        lines.append("")
        for sec in template.get("ga_sections", []):
            lines.append(f"**{sec['order']}번째 항목**")
            lines.append(f"- 제목 후보군: {' / '.join(sec.get('title_pool', []))}")
            lines.append(f"- 강조 내용: {sec.get('emphasis', '')}")
            lines.append(f"- 서술 방향: {sec.get('tone', '')}")
            if sec.get("note"):
                lines.append(f"- 구조 메모: {sec['note']}")
            lines.append("")

        lines.append("[strengths 반영 지침]")
        lines.append("- 설문의 '강점(strengths)' 항목을 기업 현황·이용목적 서술의 핵심 논거로 활용할 것")
        lines.append("  · 기업 현황 또는 이용목적 섹션의 첫 ㅇ 항목: 기업 강점을 PatSol 도입 필요성·기대 효과와 연결")
        lines.append("  · '주요 기술분야' 항목은 특허 도메인 전문성 논거로 연결하여 ❸ AI·도메인 특화 항목 점수에 기여하도록 서술")
        lines.append("  · strengths 원문을 그대로 나열하지 말고 신청서 어조에 맞게 재구성")
        lines.append("")

    elif section == "na":
        lines.append(f"[나. 세부 이용 계획 섹션 구성] — {template.get('structure_na', '')} 구조")
        lines.append("")
        for sec in template.get("na_sections", []):
            lines.append(f"**{sec['order']}번째 ㅇ 항목**")
            if sec.get("category"):
                lines.append(f"- 카테고리 제목: {sec['category']}")
            if sec.get("mapping_source"):
                lines.append(f"- 대응 한계점: {sec['mapping_source']}")
            lines.append(f"- 항목 제목: {sec.get('title', '')}")
            lines.append(f"- 강조 내용: {sec.get('emphasis', '')}")
            if sec.get("items"):
                lines.append(f"- 포함 요소: {' / '.join(sec['items'])}")
            lines.append("")

    # 공통 작성 지침
    lines.append("[작성 지침]")
    lines.append(f"- 단락 스타일: {wi.get('paragraph_style', '')}")
    lines.append(f"- 제목 변주: {wi.get('title_variation', '')}")
    if wi.get("forbidden_expressions"):
        lines.append(f"- 금지 표현: {', '.join(wi['forbidden_expressions'])}")
    if wi.get("required_elements"):
        lines.append("- 필수 포함 요소:")
        for elem in wi["required_elements"]:
            lines.append(f"  · {elem}")

    return "\n".join(lines)


# ─────────────────────────────────────────────
# 섹션별 Claude API 호출 (비동기)
# ─────────────────────────────────────────────
async def generate_section(
    client: anthropic.AsyncAnthropic,
    system_prompt: str,
    user_prompt: str,
    section_name: str,
    template_id: str,
) -> tuple[str, str]:
    """단일 섹션 생성, (section_name, content) 반환"""
    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt,
    )
    content = message.content[0].text
    return section_name, content


# ─────────────────────────────────────────────
# 단일 템플릿 초안 생성
# ─────────────────────────────────────────────
async def generate_draft(
    client: anthropic.AsyncAnthropic,
    survey: dict,
    template: dict,
    base_content: str,
) -> str:
    """템플릿 1종에 대해 섹션별 병렬 호출 → 완성 초안 반환"""
    survey_text = survey_to_text(survey)
    system_prompt = build_system_prompt()

    # 생성할 섹션 목록 (가, 나, 다, 마)
    sections = [
        ("ga", "## 가. 이용목적"),
        ("na", "## 나. 클라우드 서비스 이용계획\n\n### 2) 클라우드서비스 세부 이용 계획"),
        ("da", "## 다. 클라우드 도입 및 개선방향"),
        ("ma", "## 마. 심화컨설팅 이용계획(상세)"),
    ]

    tasks = []
    for section_key, _ in sections:
        user_prompt = build_user_prompt(survey_text, template, base_content, section_key)
        task = generate_section(client, system_prompt, user_prompt, section_key, template["id"])
        tasks.append(task)

    # 병렬 호출
    results = await asyncio.gather(*tasks)
    result_map = dict(results)

    # 섹션 조합하여 완성 초안 구성
    company_name = survey.get("company_name", "")
    now = datetime.now().strftime("%Y-%m-%d")

    draft_parts = [
        f"# 클라우드바우처 이용계획서 — {company_name}",
        f"> 템플릿: {template['id']} ({template['name']}) | 생성일: {now}",
        f"> 강조점: {template['emphasis']} | 서술방식: {template['style']} | 프레임: {template['frame']}",
        "",
        "# 2. 클라우드서비스 지원 필요성",
        "",
    ]

    for section_key, section_header in sections:
        draft_parts.append(section_header)
        draft_parts.append("")
        draft_parts.append(result_map.get(section_key, "(생성 실패)"))
        draft_parts.append("")
        draft_parts.append("---")
        draft_parts.append("")

    return "\n".join(draft_parts)


# ─────────────────────────────────────────────
# 출력 저장
# ─────────────────────────────────────────────
def save_draft(draft: str, company_name: str, template_id: str, output_dir: Path) -> Path:
    company_dir = output_dir / re.sub(r"[^\w\-_]", "_", company_name)
    company_dir.mkdir(parents=True, exist_ok=True)
    path = company_dir / f"draft_{template_id}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(draft)
    return path


# ─────────────────────────────────────────────
# 메인 실행
# ─────────────────────────────────────────────
async def main(survey_path: str, template_ids: list[str] | None, output_dir: str):
    survey = load_survey(survey_path)
    templates = load_templates(template_ids)
    base_content = load_base_content()
    out_dir = Path(output_dir)

    client = anthropic.AsyncAnthropic()  # ANTHROPIC_API_KEY 환경변수 사용

    company_name = survey.get("company_name", "unknown")
    print(f"[{company_name}] 초안 생성 시작 — {len(templates)}종 템플릿")

    # 템플릿별 순차 처리 (섹션은 각 템플릿 내에서 병렬)
    # 동시에 너무 많은 요청을 보내지 않도록 순차 처리
    for i, template in enumerate(templates, 1):
        print(f"  [{i}/{len(templates)}] {template['id']}: {template['name']} 생성 중...")
        try:
            draft = await generate_draft(client, survey, template, base_content)
            path = save_draft(draft, company_name, template["id"], out_dir)
            print(f"    → 저장: {path}")
        except Exception as e:
            print(f"    [오류] {template['id']}: {e}")

    print(f"\n완료. 결과 위치: {out_dir / company_name.replace(' ', '_')}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="클라우드바우처 이용계획서 자동 초안 생성기")
    parser.add_argument("--survey", required=True, help="설문 JSON 파일 경로")
    parser.add_argument(
        "--templates",
        default=None,
        help="생성할 템플릿 ID (쉼표 구분, 예: T01,T03,T05). 미지정 시 전체 10종",
    )
    parser.add_argument("--output-dir", default=str(OUTPUTS_DIR), help="출력 디렉토리 경로")
    args = parser.parse_args()

    template_ids = [t.strip() for t in args.templates.split(",")] if args.templates else None

    asyncio.run(main(args.survey, template_ids, args.output_dir))

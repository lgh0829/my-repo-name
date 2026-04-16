"""
클라우드바우처 신청서 자동 초안 생성기 (2026)
- 설문 입력 → Claude API 병렬 생성 → template.hwp 누름틀 채우기 → {기업명}_T01~T10.hwp 저장
"""

import asyncio
import json
import os
import random

from openai import AsyncOpenAI

try:
    import win32com.client as win32
except ImportError:
    win32 = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_HWP_PATH = os.path.join(BASE_DIR, "template2026.hwp")

# ── 10종 템플릿 (PLAN.md Phase 2) ──────────────────────────────────────────────
TEMPLATES: list[dict] = [
    {"id": "T01", "emphasis": "업무효율",    "style": "서술형", "frame": "문제→해결",   "ga": "α", "na": "α"},
    {"id": "T02", "emphasis": "비용절감",    "style": "구조형", "frame": "문제→해결",   "ga": "α", "na": "δ"},
    {"id": "T03", "emphasis": "보안",        "style": "서술형", "frame": "목적→수단",   "ga": "γ", "na": "γ"},
    {"id": "T04", "emphasis": "경쟁력",      "style": "구조형", "frame": "AS-IS/TO-BE", "ga": "δ", "na": "β"},
    {"id": "T05", "emphasis": "성장잠재력",  "style": "서술형", "frame": "목적→수단",   "ga": "β", "na": "γ"},
    {"id": "T06", "emphasis": "업무효율",    "style": "구조형", "frame": "AS-IS/TO-BE", "ga": "α", "na": "δ"},
    {"id": "T07", "emphasis": "보안+비용",   "style": "서술형", "frame": "문제→해결",   "ga": "γ", "na": "β"},
    {"id": "T08", "emphasis": "경쟁력+효율", "style": "구조형", "frame": "목적→수단",   "ga": "δ", "na": "γ"},
    {"id": "T09", "emphasis": "성장잠재력",  "style": "서술형", "frame": "AS-IS/TO-BE", "ga": "β", "na": "β"},
    {"id": "T10", "emphasis": "비용+보안",   "style": "구조형", "frame": "문제→해결",   "ga": "γ", "na": "δ"},
]

# ── 축 A: 강조점 ───────────────────────────────────────────────────────────────
EMPHASIS_GUIDE: dict[str, str] = {
    "업무효율":    "수작업 감소·처리 속도 향상·반복 업무 자동화를 핵심 가치로 강조하라.",
    "비용절감":    "IT 인프라 절감 수치(예: 25% 절감)를 전면 배치하고 ROI 관점으로 서술하라.",
    "보안":        "미공개 발명·기밀 데이터 보호, 유출 방지, 보안 감사 대응을 핵심 논거로 삼아라.",
    "경쟁력":      "특허 서비스 품질 향상, 고객 만족도 제고, 시장 내 차별화 역량을 중심으로 서술하라.",
    "성장잠재력":  "데이터 축적 → AI 고도화 → 혁신기업 성장의 중장기 로드맵을 부각하라.",
    "보안+비용":   "보안 위협과 비용 이중 부담을 동시에 해결하는 시너지 논거를 전개하라.",
    "경쟁력+효율": "경쟁력 강화를 위한 효율적 업무 체계 확립이라는 두 축을 함께 강조하라.",
    "비용+보안":   "비용 절감과 보안 강화가 동시에 달성되는 통합 솔루션으로 서술하라.",
}

# ── 축 B: 서술 방식 ────────────────────────────────────────────────────────────
STYLE_GUIDE: dict[str, str] = {
    "서술형": "단락 형식으로 서술하라. 각 소항목은 제목 이후 2~4문장의 자연스러운 서술형 단락으로 작성한다.",
    "구조형": "번호·항목 구조로 서술하라. '1) 소항목명', '가) 세부항목' 형식으로 계층을 명확히 하고, 각 항목은 1~2줄의 간결한 서술로 작성하라.",
}

# ── 축 C: 논거 프레임 ──────────────────────────────────────────────────────────
FRAME_GUIDE: dict[str, str] = {
    "문제→해결":   "현재 문제점·한계를 먼저 제시한 뒤, PatSol이 이를 해결하는 방식으로 논거를 전개하라.",
    "목적→수단":   "달성 목표를 먼저 명시한 뒤, PatSol이 그 수단임을 설명하는 순서로 서술하라.",
    "AS-IS/TO-BE": "현재 상태(AS-IS)와 PatSol 도입 후 미래 상태(TO-BE)를 명확히 대비하여 서술하라.",
}

# ── 축 D-가: 이용목적 구성 (4종) ───────────────────────────────────────────────
GA_GUIDE: dict[str, str] = {
    "α": "소항목 4개: [이용목적] → [현 업무 한계점] → [도입 필요성] → [공공지원 배경]",
    "β": "소항목 3개(간결형): [기업 현황 및 이용목적 통합] → [도입 필요성] → [공공지원 배경]",
    "γ": "소항목 4개(공공지원 선행): [이용목적] → [공공지원 배경] → [현 업무 한계점] → [도입 필요성]",
    "δ": "소항목 4개(기업 소개 선행): [기업 현황] → [이용목적] → [현 업무 한계점+도입 필요성 통합] → [공공지원 배경]",
}

# ── 축 D-나: 이용계획 구성 (4종) ───────────────────────────────────────────────
NA_GUIDE: dict[str, str] = {
    "α": "기능 나열(5개): DB통합검색 → 비교발명분석 → 청구항설계 지원 → 명세서 초안 보조 → 데이터 중앙 관리",
    "β": "워크플로우 순서(5개): [전체 업무 흐름 개요] → 선행기술조사 → 청구항 설계 → 명세서 작성 → 데이터 보안",
    "γ": "기능 카테고리(3개, AI 특화): [AI 기반 검색·분석] → [변리사 설계 지원] → [데이터 관리·보안]",
    "δ": "문제-기능 1:1 매핑: pain_points 각 항목에 대응하는 PatSol 기능을 직접 연결",
}

SUBTITLE_POOL = """
소항목 제목 변주 풀:
  이용목적류: "이용 목적" / "도입 목적" / "서비스 활용 목적" / "도입 배경 및 목적"
  한계점류: "현행 운영의 문제점" / "기존 업무 방식의 한계" / "현황 및 개선 필요성"
  필요성류: "서비스 도입의 필요성" / "클라우드 전환 필요성" / "디지털 전환 필요 배경"
  공공지원류: "정부 지원의 필요성" / "공공 지원이 필요한 이유" / "자체 도입의 한계 및 지원 필요성"
  기업현황류: "기업 비즈니스 현황" / "기업 운영 현황" / "기업 현황 및 특성"
"""

# ── 고객 상황 → 강조점 매핑 ──────────────────────────────────────────────────
# pain_points / goal 키워드 → 적합한 강조점 목록
# 여러 키워드가 같은 강조점을 가리킬 수 있고, 순위별 가중치(1순위=3점)가 합산된다.

_PAIN_MAP: list[tuple[str, list[str]]] = [
    ("수작업",  ["업무효율", "경쟁력+효율"]),
    ("수동",    ["업무효율", "경쟁력+효율"]),
    ("반복",    ["업무효율", "경쟁력+효율"]),
    ("속도",    ["업무효율", "경쟁력+효율"]),
    ("보안",    ["보안", "보안+비용", "비용+보안"]),
    ("유출",    ["보안", "보안+비용", "비용+보안"]),
    ("감사",    ["보안", "보안+비용"]),
    ("비용",    ["비용절감", "보안+비용", "비용+보안"]),
    ("지출",    ["비용절감", "비용+보안"]),
    ("예산",    ["비용절감"]),
    ("분산",    ["업무효율", "경쟁력"]),
    ("시스템",  ["업무효율", "경쟁력"]),
    ("통합",    ["업무효율", "경쟁력"]),
    ("인력",    ["업무효율", "성장잠재력"]),
    ("부재",    ["업무효율", "성장잠재력"]),
    ("경쟁",    ["경쟁력", "경쟁력+효율"]),
    ("품질",    ["경쟁력", "경쟁력+효율"]),
    ("서비스",  ["경쟁력", "성장잠재력"]),
    ("성장",    ["성장잠재력"]),
    ("확장",    ["성장잠재력", "경쟁력"]),
    ("혁신",    ["성장잠재력", "경쟁력"]),
]

_GOAL_MAP: list[tuple[str, list[str]]] = [
    ("효율",    ["업무효율", "경쟁력+효율"]),
    ("자동",    ["업무효율", "경쟁력+효율"]),
    ("경쟁력",  ["경쟁력", "경쟁력+효율"]),
    ("차별",    ["경쟁력", "경쟁력+효율"]),
    ("품질",    ["경쟁력", "경쟁력+효율"]),
    ("비용",    ["비용절감", "보안+비용", "비용+보안"]),
    ("절감",    ["비용절감", "비용+보안"]),
    ("절약",    ["비용절감"]),
    ("보안",    ["보안", "보안+비용", "비용+보안"]),
    ("안전",    ["보안", "보안+비용"]),
    ("성장",    ["성장잠재력"]),
    ("발전",    ["성장잠재력", "경쟁력"]),
    ("확장",    ["성장잠재력", "경쟁력"]),
    ("디지털",  ["성장잠재력", "경쟁력"]),
    ("혁신",    ["성장잠재력", "경쟁력"]),
]


def _select_templates(survey: dict, n: int = 3) -> list[dict]:
    """
    설문 데이터(pain_points, goal)를 분석해 적합한 템플릿을 점수화하고
    상위 그룹에서 n개를 랜덤 선택해 반환한다.
    - 1순위=3점, 2순위=2점, 3순위=1점
    - 점수가 같은 항목끼리는 랜덤 순서로 섞인다.
    """
    scores: dict[str, int] = {t["id"]: 0 for t in TEMPLATES}

    for rank, pain in enumerate(survey.get("pain_points", [])[:3]):
        w = 3 - rank  # 1순위=3, 2순위=2, 3순위=1
        for keyword, emphases in _PAIN_MAP:
            if keyword in pain:
                for t in TEMPLATES:
                    if t["emphasis"] in emphases:
                        scores[t["id"]] += w

    for rank, goal in enumerate(survey.get("goal", [])[:3]):
        w = 3 - rank
        for keyword, emphases in _GOAL_MAP:
            if keyword in goal:
                for t in TEMPLATES:
                    if t["emphasis"] in emphases:
                        scores[t["id"]] += w

    # 점수 내림차순 정렬 (같은 점수끼리는 랜덤)
    shuffled = TEMPLATES[:]
    random.shuffle(shuffled)
    ranked = sorted(shuffled, key=lambda t: scores[t["id"]], reverse=True)

    # 점수 > 0 인 후보군, 부족하면 전체에서 채움
    candidates = [t for t in ranked if scores[t["id"]] > 0] or ranked
    selected = candidates[:n]

    print(f"  [템플릿 선택] 점수: { {t['id']: scores[t['id']] for t in TEMPLATES} }")
    print(f"  [템플릿 선택] 선택됨: {[t['id'] for t in selected]}")
    return selected


SYSTEM_PROMPT = (
    "당신은 클라우드바우처 지원사업 신청서 전문 작성가입니다. "
    "특허법인의 업무 특성과 PatSol의 특허 AI 서비스(DB통합검색, 비교발명분석, 청구항설계 지원, 명세서 초안 보조)를 깊이 이해합니다. "
    "'AI 명세서 자동작성' 표현은 금지. 대신 'AI 기반 명세서 초안 지원'으로 표현하세요. "
    "마크다운 기호(**, ##, ###, #)는 절대 사용 금지. 순수 텍스트로만 작성하세요."
)

# ── PatSol 기대 수치 참고 풀 ────────────────────────────────────────────────────
PATSOL_METRICS = (
    "PatSol 도입 기대 수치 (참고용 — 실제 고객사 상황에 맞게 변형 활용):\n"
    "  출원 처리 속도 25% 향상 / 운영 비용 20% 절감 / 고객 응대 시간 40% 단축 / "
    "선행기술조사 시간 30% 단축"
)

# ── 섹션별 공식 작성요령 (신청서 가이드라인) ────────────────────────────────────
WRITING_GUIDE: dict[str, str] = {
    "business_status": (
        "ㅇ 기업의 현 비즈니스 현황(기업 소개 등)에 대해 상세히 작성\n"
        "ㅇ 제조, 서비스, IT업(서비스 개발) 등 수요기업이 추진하고 있는 사업 현황 기술\n"
        "  예) 선박부품, 고강도 철제 가공, 부품 제작 기업"
    ),
    "cloud_service_need": (
        "ㅇ 클라우드서비스 지원 필요성, 이용 목적 등 상세히 작성\n"
        "ㅇ 기업의 현 운영 환경 및 업무 방식에서 발생하는 한계점을 중심으로 작성\n"
        "  (예: 수작업 중심 운영, 시스템 분산, 인력·시간 부담 등)\n"
        "ㅇ 클라우드 서비스 도입을 통해 해결하고자 하는 주요 문제 및 개선 필요성을 명확히 제시\n"
        "ㅇ 자체 도입이 어려운 이유 등 공공 지원이 필요한 배경을 합리적으로 기술\n"
        "ㅇ 클라우드 도입이 기업의 업무 효율성, 경쟁력, 지속 가능성 제고에 미치는 영향을 중심으로 서술\n"
        "ㅇ 단순 도입 의지보다는 현황 기반의 구체적인 필요성을 중심으로 작성"
    ),
    "cloud_service_usage_plan_detail": (
        "ㅇ 클라우드 서비스별 세부 이용 계획 구체화\n"
        "ㅇ 서비스별 주요 기능, 활용 업무, 적용 대상 및 범위를 중심으로 기술\n"
        "ㅇ 각 서비스가 기업 운영 과정에서 수행하는 역할과 활용 방식을 명확히 제시"
    ),
    "as_is_to_be": (
        "ㅇ 귀사의 현재 현황(문제점, 필요성 등)을 기재 → 서비스 도입 후 개선될 상황을 명확히 구분하여 기재\n"
        "ㅇ 예시)\n"
        "  AS-IS: 제조·납품 과정이 개별 시스템 및 수작업 위주로 운영되어 공정 관리의 효율성이 낮음\n"
        "  TO-BE: 공정관리용 클라우드 서비스(MES) 도입 — 제작·납품 전 과정의 공정 흐름을 시스템으로 관리하여 업무 가시성 확보\n"
        "  AS-IS: 인력 및 행정 관리가 분산되어 있어 업무 진행 상황 파악에 한계가 있음\n"
        "  TO-BE: 인력·행정관리용 클라우드 서비스(ERP) 도입 — 인사·근태·행정 업무를 통합 관리하여 운영 효율성 강화"
    ),
    "advanced_consulting_plan_detail": (
        "ㅇ 선정평가에 참고되는 중요 항목이므로 심화컨설팅 요구사항 등 구체적으로 작성 필요\n"
        "ㅇ 단순 SaaS 솔루션 도입을 넘어 IaaS 활용을 통한 온프레미스 환경에서 네이티브 전환,\n"
        "  클라우드 환경 구축 등 목표가 있는 경우 더욱 상세하게 기재\n"
        "ㅇ 요구사항에 대한 이해를 도울 수 있는 자료가 있는 경우 신청서와 함께 별첨하여 제출\n"
        "  예) 기존 ERP 및 MES 시스템을 온프레미스 환경에서 클라우드 기반 IaaS 환경으로 전환하기 위한\n"
        "      구조 설계, 데이터 마이그레이션 방안 수립 및 보안 정책 검토를 위해 심화컨설팅을 희망"
    ),
    "expected_effects_of_cloud_adoption": (
        "ㅇ 클라우드 서비스 이용 지원 이후의 예상되는 정량, 정성적 기대효과\n"
        "ㅇ 기존 업무 운영 방식의 획기적 개선, 효율화, 생산성향상·비용절감, 이용자 편익성 향상 등 예상 효과 기재\n"
        "  예) 기존 수작업의 00% 개선, 육안 판독 대비 정확도 00% 상승 등\n"
        "ㅇ AI, 데이터 활용 등 서비스 고도화에 따른 부가 효과가 있는 경우 함께 작성"
    ),
    "performance_metrics": "",
    "future_service_usage_plan": (
        "ㅇ 사업 종료 이후 도입 클라우드 서비스의 지속 활용 계획 작성\n"
        "ㅇ 서비스 운영 고도화, 적용 범위 확대 등 중·장기 활용 방안 제시\n"
        "ㅇ 조직·업무 변화와 연계한 운영 계획 중심으로 구체적으로 기술"
    ),
}


# ── 설문 데이터 → 컨텍스트 문자열 ─────────────────────────────────────────────
def _ctx(survey: dict) -> str:
    pain = survey.get("pain_points", [])
    goal  = survey.get("goal", [])
    lines = [
        f"기업명: {survey.get('company_name', '')}",
        f"업종: {survey.get('industry', '')}",
        f"주요 업무: {survey.get('main_work', '')}",
        f"직원 수: {survey.get('employees', '')}명",
        f"주요 문제점(우선순위): {' > '.join(pain)}",
        f"목표(우선순위): {' > '.join(goal)}",
        f"클라우드 도입 준비도: {survey.get('cloud_readiness', '')}",
        f"IT 전담인력: {survey.get('it_staff', '')}",
        f"데이터 관리체계: {', '.join(survey.get('data_management', [])) if isinstance(survey.get('data_management'), list) else survey.get('data_management', '')}",
        f"도입 방식: {survey.get('cloud_method', '')}",
        f"도입 계획: {survey.get('cloud_timeline', '')}",
        f"운영시스템 수: {survey.get('it_asset_count', '')}개",
    ]
    for key, label in [
        ("revenue_scale",     "매출 규모"),
        ("key_customers",     "주요 고객 유형"),
        ("cloud_budget_amount", "예산"),
        ("current_tools",     "현재 사용 툴"),
        ("specific_concerns", "우려사항"),
        ("expected_effects",  "기대효과"),
        ("future_plans",      "향후 활용 방향"),
    ]:
        if survey.get(key):
            val = survey[key]
            lines.append(f"{label}: {' / '.join(val) if isinstance(val, list) else val}")
    return "\n".join(lines)


def _pain_rank(survey: dict) -> dict:
    return {str(i + 1): v for i, v in enumerate(survey.get("pain_points", [])[:3])}


def _goal_rank(survey: dict) -> dict:
    return {str(i + 1): v for i, v in enumerate(survey.get("goal", [])[:3])}


def _variation(tmpl: dict) -> str:
    return (
        "[템플릿 변형]\n"
        f"  강조점({tmpl['emphasis']}): {EMPHASIS_GUIDE.get(tmpl['emphasis'], '')}\n"
        f"  서술방식({tmpl['style']}): {STYLE_GUIDE[tmpl['style']]}\n"
        f"  논거프레임({tmpl['frame']}): {FRAME_GUIDE[tmpl['frame']]}\n"
        f"{SUBTITLE_POOL}"
    )


# ── 섹션별 프롬프트 빌더 ───────────────────────────────────────────────────────
def _build_prompt(survey: dict, section: str, tmpl: dict) -> str:
    ctx   = _ctx(survey)
    pain  = _pain_rank(survey)
    goal  = _goal_rank(survey)
    v     = _variation(tmpl)
    wg    = WRITING_GUIDE.get(section, "")

    if section == "business_status":
        data_mgmt = (
            ', '.join(survey.get('data_management', []))
            if isinstance(survey.get('data_management'), list)
            else survey.get('data_management', '')
        )
        return (
            f"클라우드바우처 신청서의 '기업 비즈니스 현황' 섹션을 작성하라.\n\n"
            f"[작성요령]\n{wg}\n\n"
            f"[기업 정보]\n{ctx}\n\n{v}\n\n"
            "[작성 지시]\n"
            f"- 업종({survey.get('industry','')}), 주요 업무({survey.get('main_work','')}), 직원 수({survey.get('employees','')}명)를 바탕으로 기업 현황을 사실 중심으로 서술\n"
            f"- IT 전담인력({survey.get('it_staff','')}), 데이터 관리체계({data_mgmt}), 운영시스템 수({survey.get('it_asset_count','')}개) 등 IT 현황 수치 포함\n"
            "- 이 섹션은 현재 상태 기술에 집중. PatSol 도입 효과·클라우드 필요성은 언급하지 말 것\n"
            "- 순수 텍스트, 마크다운 기호 없이 작성"
        )

    elif section == "cloud_service_need":
        return (
            f"클라우드바우처 신청서의 '클라우드 서비스 도입 필요성 및 이용목적' 섹션을 작성하라.\n\n"
            f"[작성요령]\n{wg}\n\n"
            f"[기업 정보]\n{ctx}\n\n{v}\n\n"
            f"[섹션 구성 — 가-{tmpl['ga']}]\n{GA_GUIDE[tmpl['ga']]}\n\n"
            "[작성 지시]\n"
            f"- 목표 1순위({goal.get('1','')})를 핵심 문장으로 반영\n"
            f"- 문제점 1순위({pain.get('1','')})와 연결하여 도입 필요성 서술\n"
            "- [주의] 가-δ 구성의 [기업 현황] 소항목은 앞 섹션(기업 비즈니스 현황)을 한 줄로만 요약 참조. 재서술 금지\n"
            "- [주의] PatSol 기능 나열(기능별 세부 설명)은 하지 말 것. 기능 상세는 세부 이용 계획 섹션에서 다룸\n"
            "- 순수 텍스트, 마크다운 기호 없이 작성"
        )

    elif section == "cloud_service_usage_plan_detail":
        return (
            f"클라우드바우처 신청서의 '클라우드 서비스 세부 이용 계획' 섹션을 작성하라.\n\n"
            f"[작성요령]\n{wg}\n\n"
            f"[기업 정보]\n{ctx}\n\n{v}\n\n"
            f"[섹션 구성 — 나-{tmpl['na']}]\n{NA_GUIDE[tmpl['na']]}\n\n"
            "[작성 지시]\n"
            f"- 도입 계획({survey.get('cloud_timeline','')}) 반영한 단계별 일정 포함\n"
            f"- {survey.get('cloud_method','')} 방식 명시\n"
            "- AI 초안 보조 → 변리사 최종 확정의 협업 워크플로우 포함\n"
            "- [주의] PatSol 기능 자체의 개념 설명(DB통합검색이란 무엇인지 등)은 반복하지 말 것\n"
            "- [주의] '어떤 기능을 왜 도입하는가'가 아닌 '어떤 순서로 어떻게 활용할 것인가' 중심으로 서술\n"
            "- 순수 텍스트, 마크다운 기호 없이 작성"
        )

    elif section == "as_is_to_be":
        return (
            f"클라우드바우처 신청서의 AS-IS/TO-BE 현황 분석 3쌍을 작성하라.\n\n"
            f"[작성요령]\n{wg}\n\n"
            f"[기업 정보]\n{ctx}\n\n"
            f"강조점({tmpl['emphasis']}): {EMPHASIS_GUIDE.get(tmpl['emphasis'], '')}\n\n"
            "[참고 예시 — 특허법인 기준 (그대로 쓰지 말고 기업 정보에 맞게 변형할 것)]\n"
            "AS-IS: KIPRIS·USPTO 등 복수 DB를 개별 접속 후 수작업으로 취합해 선행기술조사에 과다한 시간이 소요됨\n"
            "TO-BE: PatSol 단일 플랫폼 통합 조회 + 자연어·벡터 검색으로 선행기술조사 시간 단축 및 누락 최소화\n\n"
            "AS-IS: 선행기술조사·청구항 설계·명세서 작성이 별도 도구로 분리되어 정보 재입력 및 오류 발생\n"
            "TO-BE: 조사 결과가 청구항 설계 화면으로 직결되는 통합 워크플로우로 재입력 없이 연속 작업 가능\n\n"
            "[작성 지시]\n"
            f"- 주요 문제점 3가지({pain.get('1','')}, {pain.get('2','')}, {pain.get('3','')})를 각각 AS-IS 현황으로 구체적으로 서술\n"
            "- 각 AS-IS에 대응하는 PatSol 도입 후 TO-BE 개선 상태를 1~2문장으로 서술\n"
            "- AS-IS는 현재의 고통·비효율을 구체적 상황으로, TO-BE는 PatSol 도입 후 변화를 명확히\n"
            "- 반드시 아래 JSON 형식으로만 응답하라 (다른 텍스트 없이):\n"
            '[\n'
            '  {"as_is": "현재 AS-IS 상황 1 (구체적, 1~2문장)", "to_be": "PatSol 도입 후 TO-BE 개선 1 (1~2문장)"},\n'
            '  {"as_is": "현재 AS-IS 상황 2", "to_be": "TO-BE 개선 2"},\n'
            '  {"as_is": "현재 AS-IS 상황 3", "to_be": "TO-BE 개선 3"}\n'
            ']'
        )

    elif section == "advanced_consulting_plan_detail":
        return (
            f"클라우드바우처 신청서의 '고급 컨설팅 활용 계획' 섹션을 작성하라.\n\n"
            f"[작성요령]\n{wg}\n\n"
            f"[기업 정보]\n{ctx}\n\n{v}\n\n"
            "[작성 지시]\n"
            "- 지원 기간(2026년) 내 PatSol과 수행할 컨설팅 내용에 집중: 도입 최적화·직원 교육·초기 데이터 마이그레이션\n"
            f"- IT 전담인력({survey.get('it_staff','')}) 환경을 고려한 내부 역량 강화 방안 포함\n"
            "- [주의] 지원 종료 후 중장기 성장 로드맵(데이터 축적, AI 고도화 등)은 이 섹션에서 다루지 말 것 (향후 활용 계획 섹션에서 서술)\n"
            f"- 강조점({tmpl['emphasis']}) 관점에서 초점\n"
            "- 순수 텍스트, 마크다운 기호 없이 작성"
        )

    elif section == "expected_effects_of_cloud_adoption":
        effects = survey.get("expected_effects", [])
        effects_line = (
            f"- 고객 선택 기대효과({' / '.join(effects)})를 각각 정량·정성 효과로 구체화하여 서술\n"
            if effects else
            "- 업무 효율화·비용 절감 수치 예시 포함\n"
        )
        return (
            f"클라우드바우처 신청서의 '클라우드 도입 기대효과' 섹션을 작성하라.\n\n"
            f"[작성요령]\n{wg}\n\n"
            f"[기업 정보]\n{ctx}\n\n{v}\n\n"
            f"[참고 수치 — 변형 활용]\n{PATSOL_METRICS}\n\n"
            "[작성 지시]\n"
            f"{effects_line}"
            f"- 목표 2순위({goal.get('2','')})를 부가 기대효과로 반영\n"
            "- AI + 변리사 협업 구조의 품질 향상 효과\n"
            "- 특허 서비스 분야 선도사례 가능성 언급\n"
            "- [주의] 성과 지표 섹션에서 쓸 수치 지표와 중복되지 않도록 서술 관점을 차별화 (기대효과는 서술형, 성과지표는 측정치)\n"
            f"- 강조점({tmpl['emphasis']}) 관점 반영\n"
            "- 순수 텍스트, 마크다운 기호 없이 작성"
        )

    elif section == "performance_metrics":
        return (
            f"클라우드바우처 신청서의 성과 지표 3개를 작성하라.\n\n"
            f"[기업 정보]\n{ctx}\n\n"
            f"강조점({tmpl['emphasis']}): {EMPHASIS_GUIDE.get(tmpl['emphasis'], '')}\n\n"
            f"[참고 수치 — 변형 활용]\n{PATSOL_METRICS}\n\n"
            "[작성 지시]\n"
            f"- 목표({goal.get('1','')}, {goal.get('2','')})와 관련된 측정 가능한 성과 지표 3개 제시\n"
            "- 각 지표는 기대효과 섹션의 서술 내용과 다른 측정 관점으로 제시 (예: 시간, 건수, 비율 등 구체 단위 포함)\n"
            "- 구체적이고 달성 가능한 목표 수치 제시\n"
            "- 반드시 아래 JSON 형식으로만 응답하라:\n"
            '[\n'
            '  {"item": "성과지표명1", "target": "목표치1 (예: X% 단축)"},\n'
            '  {"item": "성과지표명2", "target": "목표치2"},\n'
            '  {"item": "성과지표명3", "target": "목표치3"}\n'
            ']'
        )

    elif section == "future_service_usage_plan":
        plans = survey.get("future_plans", [])
        plans_line = (
            f"- 고객 선택 향후 계획({' / '.join(plans)})을 중심으로 중장기 운영 방안을 구체적으로 서술\n"
            if plans else
            "- 지원 종료 후 PatSol 서비스 지속 활용 계획\n"
        )
        return (
            f"클라우드바우처 신청서의 '향후 서비스 활용 계획' 섹션을 작성하라.\n\n"
            f"[작성요령]\n{wg}\n\n"
            f"[기업 정보]\n{ctx}\n\n{v}\n\n"
            "[작성 지시]\n"
            f"{plans_line}"
            "- [주의] 지원 기간 중 컨설팅·교육 내용은 반복하지 말 것 (고급 컨설팅 섹션에서 다뤘음)\n"
            "- 데이터 축적 → AI 고도화 → 혁신기업 성장 중장기 로드맵을 이 섹션에서 구체화\n"
            "- 특허 서비스 분야 클라우드·AI 도입 선도사례 창출 계획\n"
            f"- 강조점({tmpl['emphasis']}) 관점 반영\n"
            "- 순수 텍스트, 마크다운 기호 없이 작성"
        )

    raise ValueError(f"알 수 없는 섹션: {section}")


# ── 체크박스 필드 매핑 ─────────────────────────────────────────────────────────
def _checkbox_fields(survey: dict) -> dict[str, str]:
    """설문 값 → HWP 누름틀 체크박스 필드 (선택='V', 미선택='')"""
    V = "V"
    f: dict[str, str] = {}

    # 1. 클라우드 컴퓨팅 구성 유형(현황)
    cfg = survey.get("cloud_current_config", "")
    f["cloud_configuration_on_premise"]            = V if "미도입" in cfg or "온프레미스" in cfg else ""
    f["cloud_configuration_public_private_vendor"] = V if "민간" in cfg else ""
    f["cloud_configuration_private_owned"]         = V if "자체" in cfg else ""

    # 2. 클라우드 컴퓨팅 도입 목적 (복수 선택)
    purposes = survey.get("cloud_purpose", [])
    if isinstance(purposes, str):
        purposes = [purposes]
    f["cloud_adoption_purpose_new_system"]     = V if any("신규" in p for p in purposes) else ""
    f["cloud_adoption_purpose_system_migration"] = V if any("전환" in p or "이전" in p for p in purposes) else ""
    f["cloud_adoption_purpose_service_expansion"] = V if any("확장" in p for p in purposes) else ""
    f["cloud_adoption_purpose_other"]          = V if any("기타" in p for p in purposes) else ""
    f["cloud_adoption_purpose_other_text"]     = survey.get("cloud_purpose_other_text", "")

    # 3. 클라우드 컴퓨팅 도입 준비도
    readiness = survey.get("cloud_readiness", "")
    f["cloud_readiness_review_stage"]          = V if "조사" in readiness or "검토" in readiness else ""
    f["cloud_readiness_planning_stage"]        = V if "계획" in readiness else ""
    f["cloud_readiness_design_stage"]          = V if "설계" in readiness or "준비" in readiness else ""
    f["cloud_readiness_implementation_stage"]  = V if "진행" in readiness else ""

    # 4. 클라우드 컴퓨팅 도입 방식
    method = survey.get("cloud_method", "")
    f["cloud_deployment_public"]               = V if "Public" in method or "퍼블릭" in method else ""
    f["cloud_deployment_private"]              = V if "Private" in method and "Public" not in method and "Hybrid" not in method else ""
    f["cloud_deployment_hybrid"]               = V if "Hybrid" in method or "하이브리드" in method else ""
    f["cloud_deployment_to_be_decided_by_consulting"] = V if "컨설팅" in method else ""

    # 5. 클라우드 컴퓨팅 도입 계획
    timeline = survey.get("cloud_timeline", "")
    f["cloud_adoption_schedule_already_adopted"]  = V if "기도입" in timeline else ""
    f["cloud_adoption_schedule_2026_first_half"]  = V if "상반기" in timeline else ""
    f["cloud_adoption_schedule_2026_second_half"] = V if "하반기" in timeline else ""
    f["cloud_adoption_schedule_unspecified"]      = V if "미정" in timeline else ""

    # 6. 클라우드 컴퓨팅 도입 예산 책정
    budget_status = survey.get("cloud_budget_status", "")
    f["cloud_budget_allocated"]        = V if "확정" in budget_status and "책정 중" not in budget_status else ""
    f["cloud_budget_amount"]           = survey.get("cloud_budget_amount", "") if "확정" in budget_status else ""
    f["cloud_budget_in_progress"]      = V if "책정 중" in budget_status else ""
    f["cloud_budget_after_consulting"] = V if "컨설팅" in budget_status else ""
    f["cloud_budget_not_allocated"]    = V if "않음" in budget_status or "미배정" in budget_status else ""

    # 7. IT 전담인력 유무
    it_staff = survey.get("it_staff", "")
    f["it_staff_dedicated_available"]    = V if "있음" in it_staff else ""
    f["it_staff_outsourced_maintenance"] = V if "외주" in it_staff else ""
    f["it_staff_not_available"]          = V if "부재" in it_staff or "없음" in it_staff else ""

    # 8. 데이터 관리체계 (복수 선택)
    data_list = survey.get("data_management", [])
    if isinstance(data_list, str):
        data_list = [data_list]
    data_str = " ".join(data_list)
    f["data_management_individual_storage"] = V if "개인 PC" in data_str or "USB" in data_str else ""
    f["data_management_internal_server_nas"] = V if "사내 서버" in data_str or "NAS" in data_str else ""
    f["data_management_cloud_storage"]      = V if "클라우드" in data_str or "네이버" in data_str or "구글" in data_str else ""
    f["data_management_integrated_system"]  = V if "통합" in data_str or "ERP" in data_str or "MES" in data_str else ""

    # 9. 운영시스템 규모
    f["it_asset_application_count"] = str(survey.get("it_asset_count", ""))

    return f


# ── 메인 클래스 ────────────────────────────────────────────────────────────────
class CloudDraft2026:
    TEXT_SECTIONS = [
        "business_status",
        "cloud_service_need",
        "cloud_service_usage_plan_detail",
        "as_is_to_be",
        "advanced_consulting_plan_detail",
        "expected_effects_of_cloud_adoption",
        "performance_metrics",
        "future_service_usage_plan",
    ]

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def _generate_section(
        self, survey: dict, section: str, tmpl: dict, sem: asyncio.Semaphore
    ) -> tuple[str, str]:
        async with sem:
            prompt = _build_prompt(survey, section, tmpl)
            response = await self.client.chat.completions.create(
                model="gpt-5.4-nano",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
            )
            text = response.choices[0].message.content or ""
            for sym in ("**", "###", "##", "#"):
                text = text.replace(sym, "")
            return section, text.strip()

    def _assemble_hwp_data(self, generated: dict, survey: dict) -> dict[str, str]:
        data: dict[str, str] = {}

        # 일반 텍스트 필드
        for key in ("business_status", "cloud_service_need",
                    "cloud_service_usage_plan_detail",
                    "advanced_consulting_plan_detail",
                    "expected_effects_of_cloud_adoption",
                    "future_service_usage_plan"):
            data[key] = generated.get(key, "")

        # AS-IS / TO-BE 3쌍 파싱
        try:
            pairs = json.loads(generated.get("as_is_to_be", "[]"))
        except (json.JSONDecodeError, Exception):
            pairs = []
        for i in range(3):
            p = pairs[i] if i < len(pairs) else {}
            data[f"as_is_status{i+1}"]     = p.get("as_is", "")
            data[f"to_be_improvement{i+1}"] = p.get("to_be", "")

        # 성과 지표 3개 파싱
        try:
            metrics = json.loads(generated.get("performance_metrics", "[]"))
        except (json.JSONDecodeError, Exception):
            metrics = []
        for i in range(3):
            m = metrics[i] if i < len(metrics) else {}
            data[f"performance_metric_item{i+1}"]   = m.get("item", "")
            data[f"performance_metric_target{i+1}"] = m.get("target", "")

        # 체크박스 필드 (설문 직접 매핑)
        data.update(_checkbox_fields(survey))
        return data

    @staticmethod
    def _open_hwp() -> object:
        """HWP COM 객체를 새로 생성하고 백그라운드로 실행한다."""
        
        #FilePath = f"{settingsConfig.HWP_SAVED_PATH}hwp_template.hwp"        

        hwp = win32.Dispatch("HWPFrame.HwpObject")
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        hwp.Run("FileClose")
        hwp.XHwpWindows.Item(0).Visible = False
        return hwp

    @staticmethod
    def _fill_and_save(hwp, data: dict, save_path: str) -> None:
        """열려 있는 HWP 문서에 필드값을 채우고 저장한 뒤 문서를 닫는다."""
        for field, text in data.items():
            try:
                hwp.PutFieldText(field, str(text).replace("\n", "\r\n"))
            except Exception as e:
                print(f"  [경고] 필드 '{field}': {e}")
        hwp.SaveAs(save_path, "HWP", "")
        hwp.Run("FileClose")   # 문서만 닫음 — HWP 프로세스는 유지

    def _write_all_hwp(
        self,
        jobs: list[tuple[str, dict, dict]],   # [(tmpl_id, hwp_data, tmpl_meta), ...]
        company_name: str,
    ) -> list[str]:
        """
        HWP를 한 번만 실행하여 모든 템플릿을 순서대로 처리한다.
        각 템플릿마다 Open → Fill → SaveAs → Close(문서) 반복 후 Quit.
        """
        if win32 is None:
            raise RuntimeError("win32com 없음. Windows + 한글 설치 환경에서 실행하세요.")

        output_dir = os.path.join(BASE_DIR, "outputs", company_name)
        os.makedirs(output_dir, exist_ok=True)

        hwp = self._open_hwp()
        saved: list[str] = []

        for tmpl_id, hwp_data, tmpl_meta in jobs:
            try:
                hwp.Open(TEMPLATE_HWP_PATH, "HWP", "")
                version_label = f"{tmpl_id}_{tmpl_meta['emphasis']}_{tmpl_meta['style']}"
                save_path = os.path.join(output_dir, f"{company_name}_{version_label}.hwp")
                self._fill_and_save(hwp, hwp_data, save_path)
                print(f"  [{version_label}] 저장: {save_path}")
                saved.append(save_path)
            except Exception as e:
                print(f"  [{tmpl_id}] HWP 오류: {e}")

        hwp.Quit()
        return saved

    async def make_draft(
        self,
        survey: dict,
        template_ids: list[str] | None = None,
        n_pool: int = 3,
    ) -> list[str]:
        """
        설문 데이터를 받아 HWP 초안 1개를 생성한다.
        - template_ids=None : 고객 상황에 맞는 후보 n_pool개 중 랜덤 1개 선택
        - template_ids 지정 : 해당 목록 중 랜덤 1개 선택
        """
        if template_ids:
            pool = [t for t in TEMPLATES if t["id"] in template_ids]
        else:
            pool = _select_templates(survey, n=n_pool)

        target = random.choice(pool)
        print(f"  [선택된 버전] {target['id']} | 강조점={target['emphasis']} | "
              f"서술={target['style']} | 프레임={target['frame']} | "
              f"가-{target['ga']} / 나-{target['na']}")

        n = len(self.TEXT_SECTIONS)

        # 선택된 템플릿 1개에 대해 섹션 병렬 생성
        sem = asyncio.Semaphore(10)
        flat = await asyncio.gather(*[
            self._generate_section(survey, s, target, sem)
            for s in self.TEXT_SECTIONS
        ])

        # HWP 데이터 조립
        company_name = survey.get("company_name", "고객")
        generated = dict(flat)
        hwp_data  = self._assemble_hwp_data(generated, survey)
        jobs = [(target["id"], hwp_data, target)]

        # HWP 저장
        return self._write_all_hwp(jobs, company_name)


# ── 단독 실행 테스트 ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    SAMPLE = {
        "company_name":  "특허법인 공간",
        "industry":      "특허법인",
        "main_work":     "중소기업 대상 특허 출원·선행기술조사 전문",
        "pain_points":   ["수작업 많음", "시스템 분산", "보안 우려"],
        "goal":          ["업무 효율화", "경쟁력 강화", "비용 절감"],
        "employees":     12,

        "cloud_current_config": "민간 클라우드",
        "cloud_purpose":        ["신규 시스템 도입", "서비스 확장"],
        "cloud_purpose_other_text": "",
        "cloud_readiness":      "도입 추진 계획 수립 단계",
        "cloud_method":         "Public Cloud",
        "cloud_timeline":       "2026년 상반기",
        "cloud_budget_status":  "예산이 책정되어 있음",
        "cloud_budget_amount":  "500~1,000만원",
        "it_staff":             "전담 부재",
        "data_management":      ["개인 PC, USB 개별 저장", "사내 서버 또는 NAS"],
        "it_asset_count":       15,

        "revenue_scale":    "5~50억",
        "key_customers":    "중소기업 중심",
        "current_tools":    "ChatGPT, 윈도우 공유폴더",
        "specific_concerns": "보안 감사 대응 어려움",
    }

    draft = CloudDraft2026()
    paths = asyncio.run(draft.make_draft(SAMPLE))
    print(f"\n완료: {len(paths)}개 파일")
    for p in paths:
        print(f"  {p}")

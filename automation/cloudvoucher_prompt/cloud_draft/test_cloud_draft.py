"""
클라우드바우처 초안 생성 테스트 스크립트
실행: python test_cloud_draft_2026.py
"""

import asyncio
import os
import sys

# ── API 키 설정 ────────────────────────────────────────────────────────────────
# 방법 1 (CMD): set OPENAI_API_KEY=sk-...
# 방법 2: 아래 줄 주석 해제 후 키 직접 입력
# os.environ["OPENAI_API_KEY"] = ""  # 환경변수로 설정하세요

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cloud_draft import CloudDraft2026

# ── 테스트 고객 데이터 ─────────────────────────────────────────────────────────
SURVEY = {
    # ══ 필수 A: 기업 기본 정보 ══════════════════════════════════════════════════
    "company_name": "이금희_test1",
    "industry":     "특허법인",
    "main_work":    "중소기업 대상 특허 출원·선행기술조사 전문",

    # 주요 문제점 (앞쪽 = 높은 우선순위)
    "pain_points": [
        "수작업 많음",   # 1순위
        "시스템 분산",   # 2순위
        "보안 우려",     # 3순위
    ],

    # 목표 (앞쪽 = 높은 우선순위)
    "goal": [
        "업무 효율화",   # 1순위
        "경쟁력 강화",   # 2순위
        "비용 절감",     # 3순위
    ],

    "employees": 12,

    # ══ 필수 C: 클라우드 컴퓨팅 현황 9개 항목 ═════════════════════════════════

    # 1. 클라우드 컴퓨팅 구성 유형(현황)
    #    선택지: "미도입/온프레미스" | "민간 클라우드" | "자체 클라우드"
    "cloud_current_config": "민간 클라우드",

    # 2. 클라우드 컴퓨팅 도입 목적 (복수 선택)
    #    선택지: "신규 시스템 도입" | "기존 시스템의 클라우드 전환" | "서비스 확장" | "기타"
    "cloud_purpose": ["신규 시스템 도입", "서비스 확장"],
    "cloud_purpose_other_text": "",

    # 3. 클라우드 컴퓨팅 도입 준비도
    #    선택지:
    #    "조사 또는 실무 검토 단계"
    #    "도입 추진 계획 수립 단계"
    #    "도입/전환 모델 설계 또는 전사적 도입 준비 단계"
    #    "도입/전환 진행 단계"
    "cloud_readiness": "도입 추진 계획 수립 단계",

    # 4. 클라우드 컴퓨팅 도입 방식
    #    선택지: "Public Cloud" | "Private Cloud" | "Hybrid Cloud" | "컨설팅 결과에 따라 결정 예정"
    "cloud_method": "Public Cloud",

    # 5. 클라우드 컴퓨팅 도입 계획
    #    선택지: "기도입" | "2026년 상반기" | "2026년 하반기" | "도입 일정 미정"
    "cloud_timeline": "2026년 상반기",

    # 6. 클라우드 컴퓨팅 도입 예산 책정
    #    선택지:
    #    "예산이 책정되어 있음"     → cloud_budget_amount 에 금액 입력
    #    "예산 책정 중임"
    #    "컨설팅 결과에 따라 예산 책정 예정"
    #    "예산이 책정되어 있지 않음"
    "cloud_budget_status": "예산이 책정되어 있음",
    "cloud_budget_amount": "500~1,000만원",

    # 7. IT 전담인력 유무
    #    선택지: "전담인력 있음" | "외주 유지보수" | "전담 부재"
    "it_staff": "전담 부재",

    # 8. 데이터 관리체계 (복수 선택)
    #    선택지:
    #    "개인 PC, USB 개별 저장"
    #    "사내 서버 또는 NAS"
    #    "클라우드(네이버, 구글드라이브 등)"
    #    "전사 통합관리 시스템(ERP, MES 등)"
    "data_management": ["개인 PC, USB 개별 저장", "사내 서버 또는 NAS"],

    # 9. 운영시스템(보유 IT 자산) 규모
    "it_asset_count": 15,

    # ══ 선택 D ═════════════════════════════════════════════════════════════════
    "revenue_scale":    "5~50억",         # 5억 미만 | 5~50억 | 50억 이상
    "key_customers":    "중소기업 중심",
    "current_tools":    "ChatGPT, 윈도우 공유폴더",
    "specific_concerns": "보안 감사 대응 어려움",

    # ══ 선택 E: 기대효과 (최대 3개) ═════════════════════════════════════════════
    "expected_effects": [
        "선행기술조사_시간단축",
        "수작업오류_누락감소",
        "데이터축적_출원전략고도화",
    ],

    # ══ 선택 F: 향후 활용 방향 (최대 3개) ══════════════════════════════════════
    "future_plans": [
        "구독연장_지속이용",
        "데이터기반_출원전략고도화",
        "단계적_업무자동화확장",
    ],
}


async def main():
    if not os.environ.get("OPENAI_API_KEY"):
        print("=" * 55)
        print("[오류] OPENAI_API_KEY 가 설정되지 않았습니다.")
        print()
        print("  방법 1 (CMD):")
        print("    set OPENAI_API_KEY=sk-...")
        print("    python test_cloud_draft_2026.py")
        print()
        print("  방법 2 (이 파일 8번째 줄 주석 해제 후 키 입력)")
        print("=" * 55)
        return

    draft = CloudDraft2026()
    company = SURVEY["company_name"]

    # template_ids=None → 고객 상황에 맞는 템플릿 3개 자동 선택
    # 특정 템플릿만 테스트하려면 예: template_ids = ["T01", "T03", "T07"]
    template_ids = None

    print(f"생성 시작: {company}")
    print(f"후보 풀: {'자동 선택 (상위 3종 중 랜덤 1개)' if template_ids is None else f'{template_ids} 중 랜덤 1개'}")
    print("생성 중... (약 30초~1분 소요)")
    print()

    paths = await draft.make_draft(SURVEY, template_ids=template_ids)

    print()
    print(f"완료: {len(paths)}개 파일")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    asyncio.run(main())

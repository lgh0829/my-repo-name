---
aliases: 클라우드바우처 신청서 초안 작성 워크플로우
작성일: 2026-04-20
수정일: 2026-04-20
상태: 초안
tags: cloud-voucher, workflow, automation
관련문서: [base_content.md, cloud_draft/cloud_draft.py]
상위문서:
---

# 클라우드바우처 신청서 초안 작성 워크플로우

> 특허법률사무소 고객의 클라우드바우처 지원사업 신청서 초안을 반복 가능하게 작성하는 표준 프로세스.
> 동일한 5단계를 모든 고객사에 적용한다.

---

## 최종 산출물

`~/Downloads/{회사명}_수요기업신청서_{날짜}.hwp` — dev 서버 API가 생성한 HWP 파일.

---

## 5단계 프로세스

### Step 1 — 웹 정보 수집

다음 검색어로 회사 공개 정보를 수집한다.

| 검색어 | 목적 |
|---|---|
| `"{회사명}"` | 홈페이지, 소개, 인원, 주요 업무 |
| `"{대표변리사명}" 변리사 전문분야` | 대표 프로필, 기술 분야 |
| `"{회사명}" site:{도메인}` | 공식 홈페이지 직접 탐색 |

**수집 목표**:
- 사무소 규모 (변리사 수, 총 직원 수)
- 주요 업무 영역 (기술 분야: 전기전자, 기계, 화학, SW·IT 등)
- 주요 고객 유형 (중소기업 / 대기업 / 스타트업)
- 매출 규모 (공개된 경우)
- 현재 사용 중인 IT 툴·시스템 (공개된 경우)

---

### Step 2 — KIPRIS 출원 이력 조회

KIPRIS 직접 접근은 JavaScript SPA라 불가. 다음 우회 방법을 사용한다.

1. WebSearch: `"대리인:{대표변리사명}" 특허 기술분야`
2. WebSearch: `"{회사명}" 특허 출원 PCT`
3. KIPRIS 직접 필요 시 사용자가 `https://www.kipris.or.kr` 에서 직접 조회 후 정보 전달

**수집 목표**:
- 주요 출원 기술 분야 (IPC 분류 기준)
- 연간 출원 건수 추정
- 주요 고객사 업종

---

### Step 3 — 설문 dict 작성

Step 1~2 수집 정보를 기반으로 `SURVEY` dict를 완성한다.

#### 특허법률사무소 공통 기본값 (회사별 수정 없이 재사용)

| 필드 | 기본값 |
|---|---|
| `cloud_readiness` | `"도입 추진 계획 수립 단계"` |
| `cloud_purpose` | `["신규 시스템 도입"]` |
| `cloud_method` | `"Public Cloud"` |
| `cloud_timeline` | `"2026년 하반기"` |
| `cloud_budget_status` | `"예산 책정 중임"` |
| `it_staff` | `"전담 부재"` |
| `data_management` | `["개인 PC, USB 개별 저장", "사내 서버 또는 NAS"]` |

#### 특허법률사무소 공통 pain_points 우선순위

1. `"수작업 많음"` — 선행기술조사 수동 처리
2. `"시스템 분산"` — KIPRIS·USPTO·EPO 개별 접속
3. `"보안 우려"` — 미공개 발명 데이터 관리

#### 특허법률사무소 공통 goal 우선순위

1. `"업무 효율화"`
2. `"경쟁력 강화"`
3. `"비용 절감"` 또는 `"보안 강화"` (회사 특성에 따라)

#### 회사별 맞춤 필드 (매번 조사 필요)

| 필드 | 수집 방법 |
|---|---|
| `company_name` | 기본정보 |
| `industry` | 웹 검색 |
| `main_work` | 웹 검색 + KIPRIS (2~3문장) |
| `strengths` | 웹 검색 + 대표 프로필 |
| `employees_patent` | 웹 검색 (변리사 수) |
| `employees_non_patent` | 웹 검색 / 추정 |
| `key_customers` | 웹 검색 |
| `it_asset_count` | 추정 (직원 수 × 1.5 기준) |
| `revenue_scale` | 웹 검색 (사람인·잡코리아) |
| `current_tools` | 웹 검색 / 추정 |
| `specific_concerns` | 업종 특성 + 회사 특이사항 |

---

### Step 4 — 초안 생성 (dev 서버 API 호출)

아래 curl 명령의 JSON 본문을 Step 3의 SURVEY 값으로 교체한 뒤 실행한다.

```bash
curl -s -X POST "https://dev.wandsol.kr/clouddraft/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "{회사명}",
    ... (Step 3 SURVEY dict 전체를 JSON으로 붙여넣기)
  }' \
  -o "/Users/leegh/Downloads/{회사명}_draft_raw" \
  -D - \
  --max-time 180
```

**API 정보**

| 항목 | 내용 |
|---|---|
| endpoint | `https://dev.wandsol.kr/clouddraft/generate` |
| 폼 URL (브라우저 수동 입력용) | `https://dev.wandsol.kr/write/write_draft/` |
| 응답 형식 | `application/octet-stream` (HWP 단일 파일) |
| 소요 시간 | 약 60~90초 (LLM 병렬 생성) — `--max-time 180` 권장 |
| 파일명 | 응답 헤더 `content-disposition` 참조 |

### Step 5 — 파일 rename

응답 헤더 `content-disposition`에 서버 지정 파일명이 URL 인코딩으로 포함된다.
`-D -` 플래그로 헤더를 출력에 포함시켜 확인한 뒤 rename한다.

```bash
# 예시 (아이피즈 케이스 실제 파일명)
mv "/Users/leegh/Downloads/{회사명}_draft_raw" \
   "/Users/leegh/Downloads/아이피즈 국제특허법률사무소_수요기업신청서_20260420.hwp"
```

---

## 검증 체크리스트

- [ ] `SURVEY` dict의 모든 필수 필드가 채워졌는가
- [ ] `pain_points` / `goal` 값이 `survey_form.html` 선택지와 정확히 일치하는가
- [ ] `specific_concerns`에 회사의 개별 상황(이중 거점, 보안 이슈 등)이 반영됐는가
- [ ] 평가 기준 ❸ AI 특화 활용도 대응 내용이 포함됐는가 (`base_content.md` 참조)
- [ ] 평가 기준 ❸ 선도사례 가능성 내용이 포함됐는가

---

## 고객사별 케이스

---

### Case 01 — 아이피즈 국제특허법률사무소

**기본 정보**

| 항목 | 내용 |
|---|---|
| 회사명 (한글) | 아이피즈 국제특허법률사무소 |
| 회사명 (영문) | IP-WIZ International Patent & Law Office |
| 대표변리사 | 하동엽 |
| 이메일 | handongyeop@daum.net |
| 홈페이지 | http://ip-wiz.com |
| 창원 사무소 | 경남 창원시 의창구 차룡로48번길 52, 스마트업파크 409호 |
| 서울 사무소 | 서울 강남구 강남대로62길 38, 동림빌딩 5층 |
| 설립 | 서울 2014년 / 창원 2016년 |
| 직원 수 | 약 10명 (국민연금 기준) |
| 변리사 수 | 5명 (하동엽, 최관락, 송인호, 윤형근, 최영중) |
| 매출 규모 | 약 12.2억 원 (사람인 2026.02 기준) |
| 기업 형태 | 중소기업 (개인과세사업자 2개 운영) |

**대표변리사 하동엽 프로필**

| 항목 | 내용 |
|---|---|
| 학력 | 부산대학교 전자컴퓨터공학과 (2005) |
| 자격 | 변리사 제44회 합격 (2008) |
| 경력 | 새림특허 → 인피니트 특허법인 → 경남지식재산센터 → 칸 특허법률사무소 → 아이피즈 대표 (2016~) |
| 전문분야 | 유무선통신, RF, 모바일, 회로, 디스플레이, 디지털방송, 영상처리, SW·IT |

**주요 업무 및 강점**

- 전기·전자, IT·SW, 기계, 화학 등 다분야 특허 출원·등록·심판·소송 풀서비스
- 국제 PCT 출원 및 해외 현지 로펌 네트워크 보유
- 서울 강남 + 경남 창원 이중 거점 운영 (창원 산업단지 중소제조업체 접점)
- 스마트업파크 입주 → 스타트업 고객 접점

**설문 dict (SURVEY)**

```python
SURVEY = {
    # ── 기업 기본 정보 ────────────────────────────────────────────────────────────
    "company_name": "아이피즈 국제특허법률사무소",
    "industry": "국제특허법률사무소",
    "main_work": (
        "전기·전자, IT·SW, 기계, 화학 등 다분야 기술 특허의 출원·등록·심판·소송 및 "
        "국제 PCT 출원을 전담하며, 중소기업 및 스타트업 대상으로 선행기술조사부터 "
        "청구항 설계, 명세서 작성에 이르는 전 과정을 서비스함."
    ),
    "strengths": (
        "부산대 전자컴퓨터공학 전공 대표변리사 주도의 전기·전자·IT·SW 분야 강점, "
        "서울 강남–경남 창원 이중 거점으로 수도권·영남권 동시 커버, "
        "해외 현지 로펌 네트워크 기반 PCT 출원 노하우 보유."
    ),
    "employees_patent": 5,
    "employees_non_patent": 5,
    "key_customers": "중소기업 중심",

    # ── 도입 목적 및 문제점 ───────────────────────────────────────────────────────
    "pain_points": ["수작업 많음", "시스템 분산", "보안 우려"],
    "goal": ["업무 효율화", "경쟁력 강화", "비용 절감"],

    # ── 클라우드 컴퓨팅 현황 (공통 기본값) ─────────────────────────────────────────
    "cloud_readiness": "도입 추진 계획 수립 단계",
    "cloud_purpose": ["신규 시스템 도입"],
    "cloud_method": "Public Cloud",
    "cloud_timeline": "2026년 하반기",
    "cloud_budget_status": "예산 책정 중임",
    "it_staff": "전담 부재",
    "data_management": ["개인 PC, USB 개별 저장", "사내 서버 또는 NAS"],
    "it_asset_count": 15,

    # ── 선택 항목 (맞춤) ───────────────────────────────────────────────────────────
    "revenue_scale": "5~50억",
    "current_tools": "KIPRIS, USPTO, EPO 개별 접속, 한컴오피스, 공유폴더",
    "specific_concerns": (
        "창원·서울 이중 거점 운영으로 사건 이력 및 문서의 분산 관리가 심각하며, "
        "고객의 미공개 발명 정보를 개인 PC 및 USB에 분산 보관하는 현행 방식으로 인한 "
        "보안 리스크가 높음. 변리사별로 상이한 업무 방식으로 인해 사건 인수인계 시 "
        "오류 및 정보 누락이 빈번하게 발생하고 있음."
    ),

    # ── 기대효과 및 향후 계획 ──────────────────────────────────────────────────────
    "expected_effects": [
        "선행기술조사_시간단축",
        "수작업오류_누락감소",
        "데이터축적_출원전략고도화",
    ],
    "future_plans": [
        "구독연장_지속이용",
        "사용인원_확대",
        "데이터기반_출원전략고도화",
    ],
}
```

**조사 출처**

| 출처 | URL |
|---|---|
| 아이피즈 공식 홈페이지 | http://ip-wiz.com |
| bizno (창원 사무소) | https://bizno.net/article/8671200255 |
| bizno (서울 사무소) | https://bizno.net/article/2201025278 |
| 사람인 기업정보 | https://www.saramin.co.kr (검색: 아이피즈국제특허법률사무소) |
| 하동엽 변리사 프로필 | http://ip-wiz.com/insiter.php?design_file=introduce_lawyer06.php |

---

<!-- 신규 케이스는 아래 형식으로 추가 -->
<!-- ### Case 02 — {회사명} -->

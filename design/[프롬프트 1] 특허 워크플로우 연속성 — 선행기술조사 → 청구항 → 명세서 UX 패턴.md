<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# [프롬프트 1] 특허 워크플로우 연속성 — 선행기술조사 → 청구항 → 명세서 UX 패턴

AI-assisted patent prosecution tools에서 prior art search,
claim drafting, specification writing을 하나의 연속된
워크플로우로 연결하는 UX 패턴을 조사해줘.

특히 아래를 중심으로:

1. PatSnap, Anaqua, Specifio, Lexi 등 주요 AI 특허 툴이
검색 결과에서 claim generation으로 전환하는 방식
2. 사용자가 선행기술 검토 결과를 claim 작성에
직접 활용할 수 있도록 설계된 UX 사례
3. 검색-청구항-명세서 간 컨텍스트를 유지하는
데이터 모델 또는 세션 설계 방식

AI 특허 툴들은 공통적으로 “검색 결과 → 청구항 → 명세서”를 하나의 세션으로 묶고, 검색·분석 결과를 구조화된 메타데이터로 저장해 두고 재사용하는 방향으로 진화하고 있습니다. 아래에서는 질문하신 세 가지 축에 맞춰, 현재 시장 툴들의 패턴과 거기서 뽑을 수 있는 UX/데이터 모델 인사이트를 정리합니다.[^1][^2][^3][^4][^5][^6][^7]

***

## 1. 검색 결과에서 claim generation으로 전환하는 방식

### PatSnap (Eureka / AI Drafting)

- 특허 분석/검색(Eureka) 화면에서 바로 “Draft with AI”류의 액션으로 넘어가, 선택한 문헌 세트와 검색 쿼리를 그대로 드래프팅 모듈에 넘기는 패턴.[^3][^6][^7][^1]
- 드래프팅 모듈은 prior art 분석을 기반으로, 청구범위가 기존 문헌과 부딪히는 부분을 피하도록 문언을 추천하는 방식(§102/103 리스크 하이라이트, 대체 표현 추천 등).[^2][^5][^1][^3]
- UX 상으로는 “검색 결과 리스트 + 개별 문헌 뷰”에서 사용자가 몇 개를 선택(tag/핀)한 뒤, “사용자 선택 문헌 + 발명 disclosure”를 인풋으로 claim 초안을 생성하는 플로우를 제공하는 것으로 설명됩니다.[^5][^7][^1][^3]


### Anaqua (AcclaimIP + Drafting/관리)

- AcclaimIP 자체는 prior art search 최적화에 초점이지만, 태깅 기능과 “custom information” 메타데이터를 통해 검색 단계에서 도출한 인사이트(특허성 여부, knock-out 여부)를 후속 드래프팅/포트폴리오 의사결정에 넘기도록 설계되어 있습니다.[^8][^9]
- 제품 사이트 기준으로 claim 자동 생성까지 한 화면에서 이어지지는 않지만, AcclaimIP의 태그/클러스터/쿼리 매트릭스가 워크플로우 상 “이 발명에 대해 참조해야 할 레퍼런스 세트”를 정의하는 도구로 쓰이고, 이 세트가 다른 Anaqua 모듈(출원 관리/드래프팅)에 연계되는 구조로 홍보됩니다.[^9][^8]


### Specifio

- Specifio는 “청구항 → 명세서” 자동화에 집중된 도구로, 전형적인 플로우는 사람이 준비한 claim set(Word)을 이메일/인터페이스로 보내면, 수정·보정 후 명세서 전체 초안을 돌려주는 구조입니다.[^10][^6][^11][^12]
- 일부 최근 설명에서는 invention disclosure와 prior art 분석도 입력으로 연계해 claim draft를 보완하는 기능(“prior art analysis integration”)을 언급하지만, 핵심 UX는 “이미 확정된/검토된 청구항을 입력으로 받는다”는 쪽에 가까워 prior art search UI와 claim generation UI가 한 화면에서 밀접하게 통합된 형태는 아닙니다.[^6][^11][^12][^10]


### LexisNexis (Patent Drafting + Prior Art)

- LexisNexis는 별도의 prior art research 도구(예: TotalPatent One, LexisNexis IP 검색 제품군)와 drafting 솔루션을 제공하며, “특허 출원 전 고품질 초안 작성”을 강조합니다.[^13][^4]
- 공통 메시지는 “출원 전 단계에서 prior art를 충분히 검토하고, 그 결과를 반영해 claims와 specification을 정제한다”는 것으로, 일부 제품에서는 drafting 화면에서 바로 prior art를 조회하거나, 청구항/명세서 문구에 대한 실시간 유사 문헌 하이라이트(semantic search 기반)를 제공하는 패턴이 소개됩니다.[^4][^2][^13]


### 기타 AI 툴의 대표적인 UX 패턴 (PowerPatent, DeepIP 등)

- 드래프팅 에디터에서 사용자가 타이핑할 때마다 백그라운드로 semantic prior art search를 수행하여, 유사 문언/구조가 있는 문헌을 실시간으로 플래그.[^14][^7][^2][^3][^5]
- “claim safe zone”을 시각화해서, 발명의 차별 요소(구조/기능/목적)를 지도처럼 보여주고 거기서 claim element를 선택·조합하도록 하는 패턴.[^7][^2][^14][^5]
- 예시 플로우:

1. 발명 disclosure 업로드 또는 자연어 설명 입력
2. 시스템이 관련 prior art를 자동 검색·클러스터링
3. 사용자가 핵심 문헌을 선택해 “이 문헌을 회피하는 청구항 생성” 명령
4. 생성된 청구항창에서 각 limitation 옆에 “이 limitation을 지지하거나 제약하는 prior art snippet”이 사이드 패널로 표시되는 형태.[^2][^14][^5][^7]

***

## 2. 선행기술 검토 결과를 claim 작성에 직접 활용하는 UX 사례

### a. 검색 결과를 구조화해 claim 작성 입력으로 재사용

- AcclaimIP의 태깅/클러스터링: 사용자에게 각 문헌에 “knock-out 가능성, 핵심 구성, 기술 분야, 특허성 판단” 등을 커스텀 태그로 붙이게 하고, 이 태그가 이후 워크플로우에서 필터링 조건이나 보고서 항목으로 재활용됩니다.[^8][^9]
    - 이 패턴을 claim drafting에 가져오면, “태그된 prior art의 claim element 리스트”를 자동 추출해 차별화 포인트를 제안하는 UI(예: X-ray/DeepIP류 툴에서 언급)로 자연스럽게 확장 가능합니다.[^11][^14][^7]
- PowerPatent·DeepIP·IP Author 류 도구: prior art 비교 분석에서 “유사 claim 구조 vs 발명 disclosure”를 일치표 형식으로 제시하고, 여기서 “발명 쪽에만 존재하는 요소”를 자동 하이라이트해 initial claim skeleton으로 전환하는 패턴을 강조합니다.[^14][^5][^7][^2]


### b. 에디터 내 “실시간 prior art 피드백” UX

- PowerPatent의 예시: 사용자가 “a rechargeable lithium battery with an improved electrolyte composition”이라고 입력하면, 즉시 동일/유사 표현이 등장하는 문헌을 옆에 띄우고, 해당 부분을 하이라이트해 보여줍니다.[^2]
    - 사용자는 이 뷰에서 문헌을 열람, 차별점 파악 후 claim 문언을 바로 수정할 수 있고, 수정 즉시 재검색·재평가가 이루어지는 피드백 루프를 형성합니다.[^2]
- “claim safe zone” UX: AI가 prior art 대비 영역을 지도처럼 시각화하고, 사용자가 슬라이더·토글을 통해 범위를 좁히거나 넓히면, 바로 관련 prior art·리스크 점수가 업데이트되는 인터랙티브 패턴이 제시됩니다.[^7][^14]


### c. prior art 인사이트를 명세서에 녹여 쓰도록 돕는 UX

- 특허 실무 가이드들은 prior art search 결과를 description 단계에서 “발명의 차별점 설명, 문제-해결 구조, 효과”로 적극 반영해야 한다고 강조합니다.[^15][^1]
- IP Author와 유사 AI 드래프팅 툴들은 prior art insight를 기반으로
    - “발명이 해결하는 과제” 항목에, 검색 단계에서 드러난 기존 기술의 한계·문제점을 자동 요약
    - “발명의 효과” 항목에, prior art 대비 개선점을 자동 기입
하는 식의 스캐폴딩을 제공해, 사용자가 한 번 더 검토·수정하도록 하는 플로우를 제안합니다.[^1][^15][^5][^7]

***

## 3. 검색–청구항–명세서 간 컨텍스트 유지용 데이터/세션 설계 패턴

실제 상용 툴의 내부 스키마는 공개되지 않지만, 공개 설명과 특허·블로그를 종합하면 아래와 같은 공통 설계 패턴을 추론할 수 있습니다.[^16][^12][^5][^6][^11][^1][^7][^2]

### a. “워크스페이스/프로젝트” 단위 세션

- 많은 도구들이 “invention workspace / matter / project” 단위를 기준으로
    - 발명 disclosure
    - prior art 검색 쿼리 및 결과 세트(문헌 리스트 + relevance 점수 + 클러스터 ID)
    - 사용자가 선택/태깅한 핵심 문헌
    - claim drafts 버전 히스토리
    - specification draft와 그 버전
를 하나의 엔티티 안에 묶어 관리합니다.[^3][^5][^6][^1][^8][^7]
- 세션 ID + 문맥 메타데이터(클라이언트, 기술 분야, 우선권/출원 전략 등)를 중심으로, AI 호출 기록과 프롬프트/응답 로그까지 함께 저장하는 패턴이 제안됩니다.[^5][^16][^7]


### b. prior art·claim·명세서 간 연결을 위한 데이터 구조

- Specifio 관련 문헌에서는 “claim을 데이터 구조로 파싱해, 문언 요소를 구조화(요소/관계/소프트웨어 컴포넌트 식별)한 뒤, 이를 prose 기반 데이터 구조로 변환해 명세서를 생성”하는 방식이 설명됩니다.[^12][^11]
    - 이때 각 claim element가 어떤 문단/도면 설명과 연결되는지가 데이터 구조로 유지되며, 결국 “claim ↔ 명세서 문단 ↔ 도면 요소” 간 링크가 생깁니다.[^11][^12]
- 같은 구조를 prior art까지 확장하면,
    - prior art 문헌의 claim/description에서 추출한 element 구조
    - 발명 claim 구조
를 동일한 포맷으로 표현하고, 매칭 관계(동일/유사/차별 요소)를 edge로 저장하는 그래프 모델 또는 테이블 모델이 자연스럽습니다.[^14][^5][^11][^7][^2]

예시 개념 스키마(추상화):

- Workspace
    - invention_id, client_id, tech_domain, jurisdictions …
    - disclosures[]
    - prior_art_sets[]
        - search_query, timestamp, engine, filters
        - documents[] (doc_id, score, tags[], clusters[])
    - claim_versions[]
        - claim_tree (independent/dependent 구조, 각 element의 ID)
        - element ↔ prior_art_match[] (doc_id, section, similarity_score, reason_code)
    - spec_versions[]
        - sections[] (기술분야, 배경기술, 과제, 해결수단, 효과 등)
        - section ↔ claim_element_link[]

이와 같은 구조는 “검색 단계에서의 분석 구조”를 그대로 유지하면서, claim·spec에서 어떤 부분이 어떤 prior art 인사이트에 근거해 작성되었는지 추적 가능하게 해 줍니다.[^16][^12][^5][^11][^7][^2]

### c. “전략 컨텍스트”까지 보존하는 세션 설계

- 일부 논의는, AI 도입으로 인해 발명자·변리사·비즈니스 담당자 간 대화(프롬프트·피드백)가 모두 기록되므로, 전통적으로 사라지던 “왜 이런 스코프를 선택했는가”라는 전략적 맥락을 메타데이터로 보존할 수 있다고 지적합니다.[^16]
- 제안되는 패턴:
    - 각 주요 결정(스코프 선택, 특정 prior art를 회피하는 전략, 특정 시장을 노리는 claim drafting 등)에 “decision record”를 남기고, 관련된 prior art set, claim version, spec version과 링크
    - 타임라인 뷰에서 사용자가 과거 워크플로우·결정 이유를 추적 가능하도록 하는 UI.[^5][^7][^16]

***

## 정리: UX·데이터 모델 설계 인사이트

AI 특허 워크플로우를 설계할 때, 시장 패턴에서 뽑을 수 있는 **핵심 UX/데이터 포인트**는 다음과 같습니다.[^6][^12][^1][^8][^3][^11][^7][^14][^5][^2]

- UX
    - 검색 화면에서 곧바로 “이 결과를 기반으로 claim/spec draft 생성” 액션을 제공하고, 선택한 문헌·태그를 그대로 드래프팅 모듈 인풋으로 넘긴다.
    - 드래프팅 에디터 안에 “실시간 prior art 패널”을 두어, claim 문언과 prior art 매칭 결과를 동시에 편집하도록 한다.
    - 명세서 템플릿(배경기술/과제/효과)에 prior art 분석 요약을 자동 삽입하고 사용자가 검토·수정하는 흐름을 제공한다.
- 데이터/세션
    - “워크스페이스/프로젝트” 단위로 disclosure–prior art–claims–spec–AI 대화 로그를 하나의 세션에 묶어 버전 관리.
    - claim/spec을 element 단위 데이터 구조로 파싱하고, 각 element와 prior art 매칭 정보, 그리고 관련 명세서 문단을 링크하는 그래프/테이블 모델을 설계.
    - 전략적 의사결정(스코프 설정·회피 전략)을 메타데이터로 남겨, 후속 OA 대응·continuation·해외출원에서 재활용 가능하게 한다.

이 관점에서, 만약 직접 UX 플로우/데이터 모델을 설계하신다면, 위 패턴들을 “하나의 세션 그래프 위에 prior art node, claim node, spec node, decision node가 엮여 있는 구조”로 추상화한 뒤, 각 단계 UI에서 이 그래프의 다른 부분을 슬라이스·뷰로 보여주는 쪽이 자연스러운 방향입니다.[^11][^7][^5][^16][^2]
<span style="display:none">[^17]</span>

<div align="center">⁂</div>

[^1]: https://www.patsnap.com/resources/blog/articles/how-to-make-patent-drafting-more-efficient/

[^2]: https://powerpatent.com/blog/how-claim-drafting-tools-integrate-with-prior-art-search

[^3]: https://www.patsnap.com/resources/blog/articles/ai-patent-drafting-tools-2025/

[^4]: https://www.lexisnexisip.com/solutions/patent-drafting/

[^5]: https://ipauthor.com/ai-patent-drafting-workflow/

[^6]: https://www.patsnap.com/de/resources/blog/articles/ai-patent-drafting-tools-2025/

[^7]: https://www.deepip.ai/blog/patent-drafting-ai-guide

[^8]: https://www.anaqua.com/analytics/patent-search/

[^9]: https://www.anaqua.com/resource/uncited-prior-art-enabled-by-new-citation-data/

[^10]: https://ip-lawyer-tools.com/specifio-an-automated-patent-applications-drafting-system-for-bulk-software-patents-drafting-factories/

[^11]: https://xray.greyb.com/intellectual-property/claims-drafting

[^12]: https://www.artificiallawyer.com/2017/07/28/meet-specifio-the-ai-start-up-automating-patent-drafting/

[^13]: https://www.lexisnexisip.com/resources/prior-art-research/

[^14]: https://powerpatent.com/blog/best-ai-tools-for-patent-prior-art-analysis

[^15]: https://patentpc.com/blog/how-to-conduct-a-prior-art-search-before-drafting-a-patent/

[^16]: https://www.linkedin.com/pulse/new-opportunity-using-ai-preserve-strategic-context-patent-marais-bquje

[^17]: https://ipbusinessacademy.org/summary-of-how-to-draft-patents-with-ai-webinar-by-bastian-best


# 계획 프롬프트 — 명세서 본문 클러스터 뷰어 앱

> 이 문서는 **다른 세션의 에이전트에게 그대로 전달하는 작업 지시서**다.
> 목표: 특허 명세서를 본문 작성 스타일 클러스터별로 분리하고, 각 출원의 본문 5개 항목을
> 항목별로 열람하는 간단한 화면을 만든다.

---

## 0. 너에게 주어진 미션 (한 줄)

`kr_pub_patents` / `kr_opn_patents`에 있는 특허 3,390건을 **본문 스타일 클러스터(C0~C4)**로 분류해 두고,
사용자가 **클러스터를 고르면 → 해당 출원 목록 → 출원을 고르면 → 본문 5개 항목을 항목별로** 볼 수 있는 웹 화면을 만들어라.

본문 5개 항목 = **배경기술 / 해결하려는 과제 / 과제의 해결 수단 / 발명의 효과 / 발명을 실시하기 위한 구체적인 내용(실시예)**

---

## 1. 데이터 소스 (Elasticsearch)

```
ES_URL=http://192.168.0.163:9204
ES_USERNAME=elastic
ES_PASSWORD=Rx6U8blh53KmWzs1Brnj
인덱스: kr_pub_patents, kr_opn_patents (둘 다 조회. 같은 출원번호면 pub 우선)
```

> **[절대 금지]** GET/_search 조회만 허용. DELETE·PUT·POST(색인) 금지.

### 본문 5개 항목 ↔ ES 필드 매핑

| 화면 표시명 | ES 필드 | 채움률 주의 |
|---|---|---|
| 배경기술 | `Background` | 거의 100% |
| 해결하려는 과제 | `Problem` | 94~100% |
| 과제의 해결 수단 | `SolutionProblem` | **사무소별 0~50%** — 비어있으면 "(미기재)" 표시 |
| 발명의 효과 | `Effects` | 65~99% |
| 실시예 | `Embodiment` | 100%, 평균 1.5만자(길다) |

> ❌ `TechProblem`·`TechSolution`·`AdvantageousEffects` 필드는 전부 비어 있으니 쓰지 마라.
> 메타 필드: `ApplicationNumber`(keyword), `Title`, `MainCPC`(text, CPC코드), `AgentNames`(text, `¶`로 복수 구분).
> CPC는 반드시 `MainCPC`를 써라. `CPC_MAIN`·`IPC_MAIN`은 비어 있다.

---

## 2. 분석 대상 출원 목록 (3,390건)

세 그룹으로 구성된다. 각 출원번호는 아래 기존 산출물에서 가져와라.

| 그룹 | 출원번호 출처 | 건수 |
|---|---|---|
| 김앤장(한국기업) | `ref/김앤장_한국기업_출원목록.xlsx` (컬럼 `출원번호`, `비고`!='의심'인 행만) | 1,390 |
| jang(장수길) | `output/jang_patents_1000.csv` (컬럼 `출원번호`) | 1,000 |
| leeandmok | `output/leeandmok_patents_1000.csv` (컬럼 `출원번호`) | 1,000 |

대리인 정보: 김앤장은 xlsx의 `검색된_김앤장_변리사` 컬럼(`¶` 구분), jang·leeandmok은 ES `AgentNames`에서 추출.

---

## 3. 클러스터 정의 (이미 분석 완료됨)

5개 본문 스타일 클러스터. 상세는 `output/body_style_clustering.md` 참조.

| 클러스터 | 이름 | 핵심 특성 | 주 사무소 |
|---|---|---|---|
| **C1** | JP 번역체 | 실시'형태' + 선행기술 특허문헌 인용 + 짧은 배경기술 + 간접 과제 | jang 92% |
| **C3** | JP 무효과형 | 실시'형태' + **효과 섹션 없음** | jang 77% |
| **C2** | 국내 표준 | 실시'예' + 효과 기재 + 실시형태 안 씀 | leeandmok·김앤장 공유 |
| **C4** | 배경기술 중심 | **배경기술 최장(~1,900자)** + 실시예 최단 + 직접 과제 | 김앤장(기계·건설) |
| **C0** | 장문 간접형 | 간접 과제 + 긴 실시예 | 3사 혼재(경계군) |

### 클러스터 라벨 부여 방법 — **두 옵션 중 택1**

**[권장] 옵션 A — 본문 특성 측정 후 K-means(k=5) 재현**
1. 각 출원에서 아래 12개 이진 특성 + 3개 분량 특성을 정규식으로 측정한다.
2. z-score 표준화 후 K-means(k=5, seed=42) 실행 → 라벨 부여.
3. 각 클러스터의 사무소 구성·특성 평균을 출력해 위 표(C1=jang 92% 등)와 대조해 클러스터 번호를 매핑한다.

측정 정규식 (검증 완료된 것 그대로 사용):
```python
import re
def measure(bg, prob, eff, emb):
    return {
      'cite_pat':   1 if re.search(r'특허문헌|선행기술문헌|공개특허|등록특허|특허\s*제?\s*\d|KR\s*\d{2}|특개|일본 특허|미국 특허', bg) else 0,
      'p_direct':   1 if re.search(r'문제(가|점이|점을|점도)\s*(있었|있다|발생|존재)', prob+' '+bg) else 0,
      'p_indirect': 1 if re.search(r'(요구|필요|요청)(되고|된다|되었|하고 있|성이)', prob+' '+bg) else 0,
      'multi_emb':  1 if len(re.findall(r'제\s*[1-9][0-9]?\s*(실시\s*예|실시\s*형태|구현\s*예|실시예|실시형태|구현예)', emb))>=2 else 0,
      'eff_filled': 1 if len(eff.strip())>10 else 0,
      'eff_qual':   1 if re.search(r'현저히|크게|효과적으로|용이하게|향상|개선|우수', eff) else 0,
      'sil_hyeong': 1 if re.search(r'실시\s*형태', emb) else 0,
      'sil_ye':     1 if re.search(r'실시\s*예', emb) else 0,
      'term_def':   1 if re.search(r'(본\s*명세서에서\s*사용되는\s*용어|용어의?\s*정의|본\s*발명에서\s*사용되는\s*용어)', emb[:1200]) else 0,
      'fig_list':   1 if re.search(r'도\s*\d+[은는이가]\s*.{2,20}(도|면|사시도|단면도|평면도|블록도)', emb[:800]) else 0,
      'bracket':    1 if re.search(r'\(\d+\)', emb) else 0,
      'inline':     1 if re.search(r'도\s*\d+[은는을를이가에서]', emb) else 0,
      'bg_len': len(bg), 'emb_len': len(emb), 'tf_len': 0,
    }
```

**옵션 B — 규칙 기반 (간단하지만 정확도 75%)**
K-means 없이 아래 규칙으로 분류. 단 기존 K-means 라벨과 75% 일치하며 C0를 잘 못 잡는다는 한계를 사용자에게 명시할 것.
```
if bg_len>=1500 and emb_len<11000:        → C4
elif sil_hyeong or (cite_pat and not sil_ye):
    if not eff_filled: → C3
    else: → C1
elif p_indirect and emb_len>=20000:        → C0
else:                                       → C2
```

> **분류 결과는 반드시 `output/cluster_labeled.csv`로 영구 저장**한다.
> 컬럼: `출원번호, 사무소, 대리인, MainCPC, 클러스터, 발명명칭`.
> (본문 텍스트는 용량이 크므로 CSV에 넣지 말고, 앱에서 ES 실시간 조회한다.)

---

## 4. 앱 기능 명세

### 화면 흐름
```
[클러스터 선택]  →  [출원 목록]  →  [출원 상세: 본문 5항목]
   C0~C4            테이블             탭 or 아코디언
```

### 화면 1 — 클러스터 선택
- C0~C4 카드 5개. 각 카드: 클러스터 이름 + 핵심특성 한줄 + 건수.
- (선택) 사무소·CPC 필터.

### 화면 2 — 출원 목록
- 선택 클러스터의 출원 테이블: `출원번호 | 발명명칭 | 사무소 | 대리인 | CPC`.
- 검색·정렬 가능하면 좋음.

### 화면 3 — 출원 상세 (핵심)
- 출원번호 클릭 시 ES에서 본문 5필드 실시간 조회.
- **5개 항목을 각각 구분된 영역(탭 또는 펼침 패널)으로** 표시:
  1. 배경기술 (`Background`)
  2. 해결하려는 과제 (`Problem`)
  3. 과제의 해결 수단 (`SolutionProblem`) — 비면 "(미기재)"
  4. 발명의 효과 (`Effects`)
  5. 실시예 (`Embodiment`) — 길므로 스크롤 영역
- 상단에 메타(발명명칭·출원인·CPC·대리인·소속 클러스터) 표시.
- (선택) 두 출원을 좌우로 놓고 항목별 비교하는 모드.

---

## 5. 기술 스택 (간단함 우선)

| 후보 | 적합성 |
|---|---|
| **Streamlit** (권장) | 파이썬 단일 파일, ES 조회·표·탭 모두 간단. `streamlit run app.py` |
| Flask + 정적 HTML | 더 가볍게 만들고 싶을 때 |
| FastAPI + 미니 프론트 | 비교·검색 고도화 시 |

- ES 조회는 `requests` 또는 `elasticsearch` 파이썬 클라이언트.
- `.env`에서 접속정보 로드(이미 `es-search/.env` 존재).

---

## 6. 작업 단계 (To-Do)

1. **데이터 준비**
   - 세 출처에서 출원번호 + 메타 수집 (3,390건)
   - ES 배치 조회(100건씩)로 본문 5필드 가져와 특성 측정
   - 클러스터 라벨 부여(옵션 A 권장) → `output/cluster_labeled.csv` 저장
   - 클러스터별 건수·사무소 구성 출력해 `body_style_clustering.md`와 대조 검증
2. **앱 골격**: 화면 1·2 (라벨 CSV만으로 동작)
3. **상세 화면**: 화면 3 — 출원번호로 ES 본문 5필드 조회·항목별 렌더
4. **다듬기**: 검색/필터, (선택) 비교 모드
5. **README**: 실행법 + 클러스터 정의 요약

---

## 7. 주의사항 (이미 겪은 함정 — 반복 금지)

1. **필드명**: CPC는 `MainCPC`. `CPC_MAIN`·`IPC_MAIN`은 비어 있다.
2. **`SolutionProblem`은 jang·leeandmok에서 거의 0% 채움** → "(미기재)" 정상 처리. 비었다고 오류 아님.
3. **종속/말미 파싱 불필요**: 이 앱은 본문만 다룬다. 청구항 파싱 로직은 필요 없음.
4. **정규식 측정의 함정**: 과거 "용어정의 선행"을 도면부호 규칙과 혼동해 과대 측정한 사례 있음. 측정값을 표로 출력해 눈으로 검증할 것.
5. **C0는 경계군**이라 규칙 분류가 약하다(75%). 정확도가 중요하면 옵션 A(K-means) 사용.
6. **Embodiment는 평균 1.5만자, 최대 18만자**. 화면에 한 번에 다 그리면 무겁다 → 스크롤 영역/지연 로드.
7. **개인정보**: `InventorName`(발명자명)은 화면에 표시하지 마라.
8. ES에는 **GET 조회만**. 색인·삭제 쿼리 금지.

---

## 8. 참고 산출물 (이 워크스페이스에 이미 존재)

- `output/body_style_clustering.md` — 클러스터 5종 상세 정의·프롬프트 파라미터
- `output/kimandjang_patents.csv` / `jang_patents_1000.csv` / `leeandmok_patents_1000.csv` — 출원번호·CPC
- `output/kimandjang_attorney_style.md` — 대리인별 스타일(앱 필터 아이디어)
- `CLAUDE.md` — ES 필드 목록·쿼리 규칙

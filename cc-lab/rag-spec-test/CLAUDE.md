# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 목적

특허 명세서의 **전개방식·문체**를 분석하기 위한 로컬 RAG 파이프라인 실험 공간입니다.
세 가지 문서 포맷(PDF · JSON · MD)을 같은 명세서 데이터에 적용해 임베딩 품질을 비교합니다.

분석 대상 명세서는 ES v1(`kr_pub_patents`)에서 출원번호로 조회합니다.  
출원번호 목록: `/Users/leegh/cc-workspace/es-search/output/list.csv`  
ES 접속·스키마 규칙: `/Users/leegh/cc-workspace/es-search/CLAUDE.md`

---

## 환경 설정

```bash
# 가상환경 생성 (Python 3.9 기준)
python3 -m venv .venv && source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

`requirements.txt` 에 포함할 핵심 패키지:
- `chromadb` — 로컬 벡터 스토어
- `openai` — text-embedding-3-small 임베딩 + GPT 쿼리
- `anthropic` — Claude 쿼리 (이미 시스템에 설치됨)
- `elasticsearch==8.*` — ES v1 조회 (시스템에 설치됨)
- `markdown` / `fpdf2` — MD→PDF 변환
- `python-dotenv`

`.env` 파일에 `OPENAI_API_KEY` 를 설정한다.

---

## 디렉토리 구조 (설계)

```
rag-spec-test/
├── data-sample/              ← CPC 균등 샘플 ~30건
│   ├── raw/                  ← ES 원본 JSON
│   ├── md/                   ← MD 포맷 변환본
│   ├── pdf/                  ← PDF 포맷 변환본
│   └── json/                 ← 청킹용 정제 JSON
├── data-all/                 ← 전체 수집 2,845건
│   └── raw_all/              ← ES 원본 JSON
├── chroma/
│   ├── md/                   ← MD 컬렉션 벡터 DB
│   ├── pdf/                  ← PDF 컬렉션 벡터 DB
│   └── json/                 ← JSON 컬렉션 벡터 DB
├── scripts/
│   ├── fetch.py              ← ES → data-sample/raw/ (샘플 30건)
│   ├── fetch_all.py          ← ES → data-all/raw_all/ (전체 2,845건)
│   ├── convert.py            ← raw → md / pdf / json 변환
│   ├── embed.py              ← 각 포맷을 ChromaDB에 임베딩
│   └── query.py              ← 포맷별 RAG 쿼리 & 결과 비교
├── results/                  ← 쿼리 결과 비교 리포트 (*.md)
├── requirements.txt
└── .env                      ← OPENAI_API_KEY (git에 커밋 금지)
```

---

## 실험 단계 (Phase)

### Phase 1 — 데이터 수집
`scripts/fetch.py`: `list.csv`에서 출원번호를 읽어 ES v1에서 명세서 전문(`claims`, `description`, `abstract`)을 가져와 `data/raw/<출원번호>.json`으로 저장.  
샘플링 전략: 전체 2 919건 중 CPC 대분류별로 균등 20~30건 추출.

#### Phase 1 결과 (2026-06-29)

| 구분 | 건수 |
|---|---|
| 샘플 수집 (`data-sample/raw/`) | 29건 (CPC 균등 샘플, seed=42) |
| 전체 수집 (`data-all/raw/`) | 2,845건 |
| 미조회 (ES v1 부재) | 73건 |

- 수집 필드: `Claims`, `Background`, `Problem`, `Embodiment`, `Effects`, `TechnicalField` 등 (`InventorName` 제외)
- `SolutionProblem` 필드는 일부 문서에서 비어 있음
- 재개 시 `--resume` 플래그 사용

### Phase 2 — 포맷 변환
`scripts/convert.py`: `data/raw/` → 세 포맷 각각 변환.
- **MD**: 섹션 헤더(`## 청구항`, `## 발명의 설명`)로 구분, 불필요한 태그 제거
- **JSON**: 필드별 분리(`{"section": "claims", "text": "..."}`) + 메타데이터 포함
- **PDF**: MD 변환본을 `fpdf2`로 렌더링 (한글 폰트 필요: `NanumGothic.ttf`)

### Phase 3 — 임베딩
`scripts/embed.py`: 포맷별로 청킹(chunk_size=512, overlap=64) → `text-embedding-3-small` → ChromaDB 컬렉션(`format_md`, `format_pdf`, `format_json`) 적재.

### Phase 4 — 쿼리 테스트
`scripts/query.py`: 아래 테스트 쿼리를 세 컬렉션에 동일하게 실행, top-k 결과와 LLM 답변을 `results/`에 저장.
- "이 명세서의 청구항 전개방식을 설명해줘"
- "배경기술에서 과제를 어떻게 제시하는가"
- "실시예의 문체 특징을 분석해줘"

---

## 핵심 설계 결정

| 항목 | 선택 | 이유 |
|---|---|---|
| 벡터 스토어 | ChromaDB (로컬) | 서버 불필요, 포맷별 컬렉션 분리 용이 |
| 임베딩 모델 | `text-embedding-3-small` | OpenAI 이미 연동, 한국어 지원 |
| 청킹 단위 | 512 tokens / 64 overlap | 명세서 단락 평균 길이 고려 |
| 비교 기준 | 검색 정밀도(top-k relevance) + LLM 답변 품질 | 전개방식·문체 분석 목적 |

---

## 주의사항

- ES에는 **조회만** 한다. (`/Users/leegh/cc-workspace/es-search/CLAUDE.md` 절대 규칙 상속)
- `data/raw/`의 JSON에는 발명자명(`InventorName`) 필드가 포함될 수 있으나, 변환 및 결과 리포트에서는 제외한다.
- PDF 변환 시 한글 폰트(`NanumGothic.ttf`) 경로를 `convert.py` 상단 상수로 관리한다.
- `.env`는 절대 커밋하지 않는다.

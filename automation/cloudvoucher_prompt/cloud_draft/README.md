# PatSol 클라우드바우처 신청서 자동 초안 생성기

설문 데이터를 입력하면 AI가 클라우드바우처 신청서 HWP 초안을 자동으로 생성합니다.

---

## 요구 사항

| 항목 | 내용 |
|---|---|
| OS | **Windows 전용** (HWP COM 제어 필요) |
| 한글(HWP) | 설치 필수 |
| Python | 3.12 이상 |
| uv | 패키지 관리자 |

---

## 설치

### 1. uv 설치 (없을 경우)

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 의존성 설치

```bash
cd cloud_draft
uv sync
```

> `uv sync` 한 번으로 가상환경 생성 + 패키지 설치가 완료됩니다.

### 3. pywin32 후처리 (최초 1회)

```bash
uv run python Scripts/pywin32_postinstall.py -install
```

---

## 실행

### 웹 서버 (권장)

```bash
uv run python server.py
```

브라우저에서 `http://localhost:11000` 접속 → 폼 작성 → **초안 생성하기** 클릭 → HWP 파일 자동 다운로드

### 로컬 테스트 스크립트

```bash
uv run python test_cloud_draft.py
```

`test_cloud_draft.py` 상단의 `SURVEY` 딕셔너리에 고객 정보를 입력한 뒤 실행합니다.

---

## 파일 구조

```
cloud_draft/
├── cloud_draft.py       # 핵심 엔진 (템플릿 선택, AI 생성, HWP 저장)
├── server.py            # FastAPI 웹 서버
├── survey_form.html     # 고객 입력 폼 (서버가 서빙)
├── test_cloud_draft.py  # 로컬 테스트용 스크립트
├── template2026.hwp     # HWP 누름틀 템플릿 (필수)
├── pyproject.toml       # 의존성 정의
├── uv.lock              # 고정된 패키지 버전 (재현 가능한 설치)
├── PLAN.md              # 시스템 설계 문서
└── outputs/             # 생성된 초안 저장 위치
    └── {기업명}/
        └── {기업명}_{템플릿ID}_{강조점}_{서술방식}.hwp
```

---

## 동작 방식

```
고객 설문 입력 (웹 폼)
        ↓
고객 상황 분석 → 10종 템플릿 중 최적 후보 3개 선정
        ↓
후보 중 1개 랜덤 선택
        ↓
8개 섹션 병렬 AI 생성 (OpenAI API)
        ↓
template2026.hwp 누름틀 채우기 (HWP COM)
        ↓
outputs/{기업명}/ 에 HWP 파일 저장 → 다운로드
```

---

## 환경 변수 / API 키

`server.py` 상단에서 직접 설정합니다.

```python
os.environ["OPENAI_API_KEY"] = "sk-..."
```

---

## 자주 발생하는 오류

| 오류 | 원인 | 해결 |
|---|---|---|
| `win32com 없음` | pywin32 미설치 | `uv sync` 후 pywin32 후처리 실행 |
| `OPENAI_API_KEY` 오류 | API 키 미설정 | `server.py` 상단에 키 입력 |
| HWP 접근 허용 창 | HWP 보안 설정 | `SetMessageBoxMode(0xFFFFFFFF)` 적용됨 (자동 처리) |
| 500 Internal Server Error | 생성 중 예외 | 서버 콘솔의 `ERROR:` 로그 확인 |

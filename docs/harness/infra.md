# 인프라 관리

**트리거**: 새 서비스 연동, 스크립트 실행 환경 설정, .claude 에이전트·커맨드 추가, 인프라 장애 대응 시.

---

## 서비스 목록

### Elasticsearch

| 버전 | URL | 인덱스 | 스키마 |
|---|---|---|---|
| v2 (신규) | `http://192.168.0.7:9207` | `patent_*` | 중첩 (nested) — 평탄 쿼리 금지 |
| v1 (구형) | `http://192.168.0.163:9204` | `kr_pub_patents`, `kr_opn_patents` | 평탄 (flat) |

- 인증: `elastic` / `88888888` (v2), `elastic` / `Rx6U8blh53KmWzs1Brnj` (v1)
- **읽기 전용**: DELETE·UPDATE·인덱싱 목적 POST·매핑 목적 PUT 금지
- 스키마 상세: `es-search/docs/harness/es_schema_v2.md` / `es_schema_v1.md`

### Jira (Atlassian)

- URL: `https://patsol.atlassian.net`
- 프로젝트: `PS`
- 연동: `atlassian` MCP 서버
- **쓰기는 승인 후**: 초안 채팅 표시 → 승인 → MCP 실행

### Claude API

- SDK: `anthropic` Python 패키지
- 모델 ID 확인: `/claude-api` 스킬 (메모리 추정 금지)
- 기본 모델 전략:
  - 배치·분류: `claude-haiku-4-5-20251001`
  - 문서 생성·분석: `claude-sonnet-4-6`
  - 복잡 추론: `claude-opus-4-8`

---

## .claude/ 에이전트 · 커맨드

### 에이전트 (`/.claude/agents/`)

| 에이전트 | 역할 |
|---|---|
| `kipo-reviewer` | 특허 명세서 기재요건 심사 (KIPO 기준) |
| `prompt-engineer` | 프롬프트 설계 및 개선 |
| `gpt` | 대화 맥락 요약 → GPT 전달 |
| `meeting` | 오디오 파일 → 회의록 생성 |
| `secretary` | 회의록/태스크 → 주간 작업 스케줄 |

에이전트 추가 시: `.claude/agents/{이름}.md` 생성, frontmatter에 `name` / `description` / `tools` / `model` 명시.

### 커맨드 (`/.claude/commands/`)

| 커맨드 | 역할 |
|---|---|
| `gpt` | GPT 연동 슬래시 커맨드 |
| `meeting` | 회의록 생성 커맨드 |
| `secretary` | 스케줄 생성 커맨드 |

커맨드 추가 시: `.claude/commands/{이름}.md` 생성. 커맨드는 자동 `/` 접두어로 호출.

---

## Python 실행 환경

| 도구 | 사용 기준 |
|---|---|
| `uv` | 신규 프로젝트, playwright 포함, pyproject.toml 있을 때 |
| `pip` | 단순 스크립트, requirements.txt 있을 때 |

- Python 최소 버전: 3.9
- 가상환경: uv는 자동 관리. pip는 `venv` 또는 시스템 환경.

---

## 시크릿 관리

- 실제 시크릿: `.env.{프로젝트}` — **절대 커밋 금지**
- 커밋 허용: `.env.{프로젝트}.example` (키 목록만, 값 없음)
- `.gitignore` 패턴 확인:
  ```
  .env
  .env.*
  !.env.*.example
  ```

---

## 인프라 변경 절차

1. 새 서비스 추가: 이 파일(`infra.md`)에 서비스 항목 추가
2. 에이전트·커맨드 추가: `.claude/agents/` 또는 `.claude/commands/`에 파일 생성 + 이 파일 에이전트 표에 등록
3. 모델 변경: `claude-api` 스킬로 최신 ID 확인 후 반영
4. ES 스키마 변경: `es-search/docs/harness/es_schema_*.md` 업데이트 후 이 파일 서비스 표 갱신
5. 모든 변경은 커밋 전 사용자 확인

---

## 장애 대응 패턴

| 증상 | 확인 항목 |
|---|---|
| ES 연결 실패 | v1·v2 URL 구분, VPN/네트워크 상태 |
| Claude API 오류 | API 키 환경 변수 로드 여부, 모델 ID 유효성 |
| Jira MCP 쓰기 실패 | atlassian MCP 연결 여부, 토큰 만료 |
| uv run 실패 | `uv sync` 먼저 실행, Python 버전 확인 |

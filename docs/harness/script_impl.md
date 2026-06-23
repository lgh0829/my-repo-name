# 스크립트 구현

**트리거**: 자동화 스크립트 신규 작성, 기존 스크립트 수정, 파이프라인 추가 시.

---

## 디렉토리 결정

| 성격 | 위치 |
|---|---|
| 단일 파일 유틸리티 | `automation/scripts/auto-{주제}.py` |
| LLM 파이프라인 | `automation/scripts/pipeline-{주제}.py` |
| 멀티파일 프로젝트 | `automation/{프로젝트명}/` (자체 pyproject.toml) |
| 프롬프트 파일 | `automation/prompts/prompt-{주제}.md` |

---

## 의존성 관리

**uv (권장)** — 멀티파일 프로젝트 또는 playwright 포함 시:

```toml
# pyproject.toml
[project]
name = "{프로젝트명}"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    "anthropic>=0.30",
    "python-dotenv>=1.0",
]

[tool.uv]
package = false
```

실행: `uv sync && uv run python script.py`

**pip + requirements.txt** — 단순 스크립트:

```
anthropic>=0.30
python-dotenv>=1.0
```

실행: `pip install -r requirements.txt && python script.py`

---

## 스크립트 기본 구조

```python
#!/usr/bin/env python3
"""
{스크립트 한줄 설명}

사용법:
  python auto-{주제}.py                   # 대화형 입력
  python auto-{주제}.py input.md          # 파일 입력
  echo "내용" | python auto-{주제}.py    # 파이프 입력
"""
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import anthropic

load_dotenv(Path(__file__).parent / ".env.{주제}")

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", help="입력 파일 경로")
    args = parser.parse_args()

    if args.input:
        text = Path(args.input).read_text()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        # 대화형 입력
        ...

if __name__ == "__main__":
    main()
```

---

## Claude API 모델 선택

| 용도 | 모델 ID |
|---|---|
| 배치·대량 처리 (빠르고 저렴) | `claude-haiku-4-5-20251001` |
| 품질 우선 (분석·생성) | `claude-sonnet-4-6` |
| 고난이도 추론 | `claude-opus-4-8` |

모델 ID는 `claude-api` 스킬로 최신 목록을 확인한다. 메모리에서 추정하지 않는다.

---

## 환경 변수 패턴

- `.env.{프로젝트}` — 실제 시크릿 (커밋 금지, `.gitignore`에 추가)
- `.env.{프로젝트}.example` — 키 목록만 커밋

```bash
# .env.example
ANTHROPIC_API_KEY=your_key_here
JIRA_BASE_URL=https://patsol.atlassian.net
JIRA_EMAIL=
JIRA_API_TOKEN=
```

---

## Jira API 연동

- Base URL: `https://patsol.atlassian.net`
- 인증: Basic Auth (`{email}:{api_token}` → base64)
- 프로젝트: `PS`
- 쓰기 작업은 **항상 채팅에 초안 표시 후 승인받고 실행** (roadmap/CLAUDE.md 절대 규칙)

---

## 출력 파일 규칙

- 리포트: `output/{주제}.md` 또는 `output/{주제}.csv`
- 중간 결과: `output/tmp-{주제}.json` (필요 시)
- stdout 출력이 기본 — 파일 저장은 `--out` 플래그로 명시적으로

---

## 체크리스트

- [ ] `.env.example` 커밋 여부 확인
- [ ] `.gitignore`에 `.env.*` (example 제외) 패턴 포함 여부
- [ ] `argparse` + stdin 양쪽 입력 지원
- [ ] `output/` 디렉토리 존재 여부 확인 후 생성 (`output_dir.mkdir(exist_ok=True)`)
- [ ] 스크립트 상단 docstring에 사용법 포함

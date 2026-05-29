#!/usr/bin/env python3
"""
Secretary Agent
회의록·태스크·Jira 이슈 입력 → 우선순위 계산 → 작업 스케줄 생성 → Jira 이슈 생성

사용법:
  python secretary_agent.py                        # 대화형 입력
  python secretary_agent.py meeting_notes.md       # 파일 입력
  echo "내용" | python secretary_agent.py          # 파이프 입력
"""

import json
import os
import sys
import base64
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

from dotenv import load_dotenv
import anthropic

# ---------------------------------------------------------------------------
# 설정 로드
# ---------------------------------------------------------------------------

_ENV_FILE = os.path.join(os.path.dirname(__file__), ".env.secretary")
load_dotenv(_ENV_FILE)

ANTHROPIC_API_KEY     = os.environ.get("ANTHROPIC_API_KEY", "")
JIRA_BASE_URL         = os.environ.get("JIRA_BASE_URL", "https://patsol.atlassian.net")
JIRA_EMAIL            = os.environ.get("JIRA_EMAIL", "")
JIRA_API_TOKEN        = os.environ.get("JIRA_API_TOKEN", "")
JIRA_DEFAULT_PROJECT  = os.environ.get("JIRA_DEFAULT_PROJECT", "PS")
WORK_HOURS_PER_DAY    = int(os.environ.get("WORK_HOURS_PER_DAY", "6"))

JIRA_ENABLED = bool(JIRA_EMAIL and JIRA_API_TOKEN)

# ---------------------------------------------------------------------------
# Jira REST API helpers
# ---------------------------------------------------------------------------

def _jira_headers() -> dict:
    creds = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode()).decode()
    return {
        "Authorization": f"Basic {creds}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

def _jira_get(path: str) -> dict:
    url = f"{JIRA_BASE_URL}/rest/api/3{path}"
    req = urllib.request.Request(url, headers=_jira_headers())
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "message": e.read().decode()[:300]}
    except Exception as e:
        return {"_error": "network", "message": str(e)}

def _jira_post(path: str, body: dict) -> dict:
    url = f"{JIRA_BASE_URL}/rest/api/3{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=_jira_headers(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "message": e.read().decode()[:300]}
    except Exception as e:
        return {"_error": "network", "message": str(e)}

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def tool_get_current_datetime(_args: dict) -> str:
    now = datetime.now()
    weekday_ko = ["월", "화", "수", "목", "금", "토", "일"][now.weekday()]
    return json.dumps({
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "weekday": weekday_ko,
        "iso": now.isoformat(),
        "work_hours_per_day": WORK_HOURS_PER_DAY,
        "jira_enabled": JIRA_ENABLED,
    }, ensure_ascii=False)


def tool_fetch_jira_issues(args: dict) -> str:
    if not JIRA_ENABLED:
        return json.dumps({"_error": "Jira 자격증명이 설정되지 않았습니다. .env.secretary를 확인하세요."})
    project = args.get("project", JIRA_DEFAULT_PROJECT)
    jql = args.get("jql") or (
        f"project = {project} AND status != Done "
        "ORDER BY priority DESC, updated DESC"
    )
    max_results = min(int(args.get("max_results", 20)), 50)
    encoded_jql = urllib.parse.quote(jql)
    result = _jira_get(
        f"/search?jql={encoded_jql}"
        f"&maxResults={max_results}"
        "&fields=summary,status,priority,assignee,duedate,issuetype"
    )
    if "_error" in result:
        return json.dumps({"_error": result})
    issues = []
    for i in result.get("issues", []):
        f = i.get("fields", {})
        issues.append({
            "key": i["key"],
            "summary": f.get("summary", ""),
            "status": (f.get("status") or {}).get("name", ""),
            "priority": (f.get("priority") or {}).get("name", ""),
            "issue_type": (f.get("issuetype") or {}).get("name", ""),
            "assignee": (f.get("assignee") or {}).get("displayName", "미지정"),
            "duedate": f.get("duedate") or "",
        })
    return json.dumps({"issues": issues, "total": result.get("total", 0)}, ensure_ascii=False)


def tool_get_jira_issue(args: dict) -> str:
    if not JIRA_ENABLED:
        return json.dumps({"_error": "Jira 자격증명이 설정되지 않았습니다."})
    key = args.get("issue_key", "")
    if not key:
        return json.dumps({"_error": "issue_key가 필요합니다."})
    result = _jira_get(
        f"/issue/{key}"
        "?fields=summary,status,priority,assignee,duedate,description,subtasks,parent,issuetype"
    )
    if "_error" in result:
        return json.dumps({"_error": result})
    f = result.get("fields", {})
    desc = f.get("description")
    desc_text = ""
    if isinstance(desc, dict):
        for block in (desc.get("content") or []):
            for inline in (block.get("content") or []):
                if inline.get("type") == "text":
                    desc_text += inline.get("text", "")
    desc_text = desc_text[:400]
    return json.dumps({
        "key": result["key"],
        "summary": f.get("summary", ""),
        "status": (f.get("status") or {}).get("name", ""),
        "priority": (f.get("priority") or {}).get("name", ""),
        "issue_type": (f.get("issuetype") or {}).get("name", ""),
        "assignee": (f.get("assignee") or {}).get("displayName", "미지정"),
        "duedate": f.get("duedate") or "",
        "description_preview": desc_text,
    }, ensure_ascii=False)


def tool_create_jira_issue(args: dict) -> str:
    if not JIRA_ENABLED:
        return json.dumps({"_error": "Jira 자격증명이 설정되지 않았습니다."})
    project  = args.get("project", JIRA_DEFAULT_PROJECT)
    summary  = args.get("summary", "")
    desc     = args.get("description", "")
    itype    = args.get("issue_type", "Task")
    priority = args.get("priority", "Medium")
    due_date = args.get("due_date", "")

    body: dict = {
        "fields": {
            "project":     {"key": project},
            "summary":     summary,
            "issuetype":   {"name": itype},
            "priority":    {"name": priority},
            "description": {
                "type": "doc", "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": desc}]}],
            },
        }
    }
    if due_date:
        body["fields"]["duedate"] = due_date

    result = _jira_post("/issue", body)
    if "_error" in result:
        return json.dumps({"_error": result})
    key = result.get("key", "")
    return json.dumps({
        "created": True,
        "key": key,
        "url": f"{JIRA_BASE_URL}/browse/{key}",
    }, ensure_ascii=False)

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

TOOL_REGISTRY = {
    "get_current_datetime": tool_get_current_datetime,
    "fetch_jira_issues":    tool_fetch_jira_issues,
    "get_jira_issue":       tool_get_jira_issue,
    "create_jira_issue":    tool_create_jira_issue,
}

TOOLS = [
    {
        "name": "get_current_datetime",
        "description": (
            "현재 날짜·시간·요일과 하루 가용 작업 시간을 반환합니다. "
            "스케줄 계산의 기준점으로 사용하세요. Jira 연동 여부도 확인할 수 있습니다."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "fetch_jira_issues",
        "description": (
            "Jira 프로젝트의 미완료 이슈 목록을 가져옵니다. "
            "기존 태스크와 중복 여부를 확인하거나 컨텍스트 파악에 사용하세요."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": f"Jira 프로젝트 키 (기본값: {JIRA_DEFAULT_PROJECT})",
                },
                "jql": {
                    "type": "string",
                    "description": "JQL 쿼리 (선택). 예: 'assignee = currentUser() AND status != Done'",
                },
                "max_results": {
                    "type": "integer",
                    "description": "최대 결과 수 (기본값: 20, 최대 50)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_jira_issue",
        "description": "특정 Jira 이슈의 상세 정보를 가져옵니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "issue_key": {
                    "type": "string",
                    "description": "Jira 이슈 키. 예: PS-308",
                }
            },
            "required": ["issue_key"],
        },
    },
    {
        "name": "create_jira_issue",
        "description": (
            "새로운 Jira 이슈를 생성합니다. "
            "반드시 사용자에게 생성 목록을 먼저 보여주고 확인을 받은 후에만 호출하세요."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "이슈 제목 (간결하게, 50자 이내 권장)",
                },
                "description": {
                    "type": "string",
                    "description": "이슈 상세 설명 (배경·목적·완료 조건 포함)",
                },
                "issue_type": {
                    "type": "string",
                    "enum": ["Task", "Story", "Bug", "Epic"],
                    "description": "이슈 유형 (기본값: Task)",
                },
                "priority": {
                    "type": "string",
                    "enum": ["Highest", "High", "Medium", "Low", "Lowest"],
                    "description": "우선순위 (urgency score 기준 자동 결정)",
                },
                "due_date": {
                    "type": "string",
                    "description": "마감일 (YYYY-MM-DD 형식)",
                },
                "project": {
                    "type": "string",
                    "description": f"프로젝트 키 (기본값: {JIRA_DEFAULT_PROJECT})",
                },
            },
            "required": ["summary"],
        },
    },
]

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = f"""당신은 Wand 팀의 AI 비서 에이전트입니다.
회의록, 태스크 목록, Jira 이슈 등 다양한 업무 입력을 받아 우선순위를 계산하고 주간 작업 계획을 세워줍니다.

---

## 작동 순서

**Step 1 — 현재 시각 확인**
get_current_datetime을 가장 먼저 호출해 오늘 날짜와 Jira 연동 여부를 확인합니다.

**Step 2 — Jira 현황 파악 (Jira 연동 시)**
fetch_jira_issues로 현재 미완료 이슈를 가져와 입력된 태스크와 중복 여부를 확인합니다.
입력에 PS-XXX 형태의 이슈 키가 있으면 get_jira_issue로 상세 내용을 확인합니다.

**Step 3 — 태스크 추출 및 urgency score 계산**
입력에서 실행 가능한 액션 아이템을 모두 추출하고 아래 기준으로 urgency score(0–100)를 계산합니다.

| 항목 | 배점 | 기준 |
|---|---|---|
| 마감 긴박도 | 50점 | 오늘=50 / 2일=45 / 3일=40 / 1주=30 / 2주=20 / 미정=10 |
| 영향도 | 30점 | 외부 약속·출시·거래처=30 / 팀 블로킹=25 / 내부 리뷰=15 / 개인 작업=10 |
| 의존성 | 20점 | 타인이 기다림=20 / 다른 작업을 블록=15 / 독립=5 |

**Step 4 — 작업 스케줄 생성**
urgency score 내림차순으로 오늘부터 날짜별 타임블록을 배정합니다.
- 하루 가용 시간: {WORK_HOURS_PER_DAY}시간 (09:00–18:00, 점심 1시간 제외)
- 태스크당 예상 시간: 간단(메일·확인)=0.5h / 보통(분석·작성)=2h / 복잡(개발·설계)=4–8h

**Step 5 — Jira 이슈 생성 제안**
Jira 이슈가 없는 태스크 중 등록이 필요한 항목을 목록으로 보여주고 사용자 확인을 기다립니다.
사용자가 승인하면 create_jira_issue를 호출합니다.
priority는 urgency score 기준: 80↑=Highest / 60↑=High / 40↑=Medium / 20↑=Low / 미만=Lowest

---

## 출력 형식

### 📋 태스크 목록
urgency score 내림차순 테이블:
| # | 태스크 | 담당자 | 마감 | 예상 시간 | Urgency | Jira |
|---|---|---|---|---|---|---|

### 📅 작업 스케줄
날짜별 타임블록:
```
YYYY-MM-DD (요일)  [가용: Xh]
  HH:MM–HH:MM  태스크명  (Xh)  — 이유 한 줄
  HH:MM–HH:MM  태스크명  (Xh)
```

### 🎫 Jira 이슈 생성 제안 (해당 시)
등록 제안 목록 표시 후: "위 항목을 Jira에 생성할까요? (전체/번호 선택/취소)"

---

## 주의사항
- create_jira_issue는 반드시 사용자 확인 후 호출
- 마감일 미정 태스크는 urgency 10으로 스케줄 후반에 배치
- 담당자가 명시된 경우 태스크에 포함, 미명시는 "미정"
- Jira 연동이 안 된 경우에도 태스크 목록과 스케줄은 정상 출력
"""

# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------

def _sep(char: str = "─", width: int = 60) -> None:
    print(char * width)


def _confirm_jira_create(tool_input: dict) -> bool:
    """Jira 이슈 생성 전 사용자 확인."""
    priority = tool_input.get("priority", "Medium")
    summary  = tool_input.get("summary", "")
    due      = tool_input.get("due_date", "없음")
    itype    = tool_input.get("issue_type", "Task")
    desc     = tool_input.get("description", "")[:80]

    print()
    print("  ┌─ Jira 이슈 생성 확인 ─────────────────────────────")
    print(f"  │  유형: {itype}  |  우선순위: {priority}  |  마감: {due}")
    print(f"  │  제목: {summary}")
    if desc:
        print(f"  │  설명: {desc}...")
    print("  └───────────────────────────────────────────────────")

    answer = input("  생성하시겠습니까? (y/n): ").strip().lower()
    return answer == "y"


def run_agent(user_input: str) -> None:
    if not ANTHROPIC_API_KEY:
        print("오류: ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        print(f"  → {_ENV_FILE} 파일을 확인하세요.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    messages = [{"role": "user", "content": user_input}]

    _sep("═")
    print("🤖  Secretary Agent 분석 시작")
    _sep("═")
    print()

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        tool_blocks = [b for b in response.content if b.type == "tool_use"]
        text_blocks = [b for b in response.content if b.type == "text"]

        # Print text output
        for block in text_blocks:
            print(block.text)

        if response.stop_reason == "end_turn" or not tool_blocks:
            break

        # Process tool calls
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in tool_blocks:
            name  = block.name
            args  = block.input

            if name == "create_jira_issue":
                approved = _confirm_jira_create(args)
                if not approved:
                    result = json.dumps(
                        {"skipped": True, "reason": "사용자가 생성을 취소했습니다."},
                        ensure_ascii=False,
                    )
                    print("  → 건너뜀\n")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
                    continue
                print(f"  → 생성 중...", end=" ", flush=True)
            else:
                label = {
                    "get_current_datetime": "현재 시각 확인",
                    "fetch_jira_issues":    "Jira 이슈 목록 조회",
                    "get_jira_issue":       f"Jira 이슈 조회 ({args.get('issue_key', '')})",
                }.get(name, name)
                print(f"⚙️   {label}...", end=" ", flush=True)

            result = TOOL_REGISTRY[name](args)
            print("완료")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        print()
        messages.append({"role": "user", "content": tool_results})

    print()
    _sep("═")
    print("✅  분석 완료")
    _sep("═")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                user_input = f.read()
            print(f"📄  파일 입력: {input_path}\n")
        except FileNotFoundError:
            print(f"오류: 파일을 찾을 수 없습니다 — {input_path}")
            sys.exit(1)
    elif not sys.stdin.isatty():
        user_input = sys.stdin.read()
        print("📄  표준 입력을 분석합니다.\n")
    else:
        print("회의록, 태스크 목록, Jira 이슈 등을 입력하세요.")
        print("입력 완료 후 Ctrl+D를 누르세요.\n")
        try:
            user_input = sys.stdin.read()
        except KeyboardInterrupt:
            print("\n취소되었습니다.")
            sys.exit(0)

    if not user_input.strip():
        print("입력 내용이 없습니다.")
        sys.exit(1)

    run_agent(user_input)


if __name__ == "__main__":
    main()

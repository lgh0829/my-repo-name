"""채팅 수동 테스트 REPL (PS-976 개발용 — 운영 코드 아님).

로컬 gw 서버의 POST /api/v1/chat SSE 를 터미널에서 대화형으로 테스트한다.
JWT 는 .env 의 DJANGO_SECRET 으로 직접 서명하므로 Django 로그인이 필요 없다.

사용 (gw 레포 안에서 — .env 의 DJANGO_SECRET 으로 토큰 자동 서명):
    uv run uvicorn src.main:app --reload --port 8003   # 서버 (별도 터미널)
    uv run python scripts/chat_repl.py                 # 기본: user_id=1, localhost:8003
    uv run python scripts/chat_repl.py --user-id 7

사용 (배포용 사본을 받은 팀원 — httpx 만 있으면 됨):
    pip install httpx
    python chat_repl.py            # 배포용 사본은 dev 서버·테스트 계정 토큰이 내장됨
    # 토큰 미내장 파일이면: python chat_repl.py --token <PatSol dev 로그인 JWT>

REPL 명령:
    /new          새 대화 시작 (conversation_id 리셋)
    /claim 123    이후 메시지에 claim_id 포함 (/claim 으로 해제)
    /doc 45       이후 메시지에 document_id 포함 (/doc 으로 해제)
    /quit         종료 (Ctrl+D 동일)

스트리밍 중 Ctrl+C: 현재 응답만 중단 → 서버 partial-save(stopped_by_user) 동작 확인용.
"""

from __future__ import annotations

import sys
import json
import argparse
from pathlib import Path

import httpx

# 배포용 사본 생성 시 여기에 dev 테스트 계정 JWT 가 주입된다 (레포 버전은 빈 값 유지 — 커밋 금지)
DEFAULT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6ImNoYXQtdGVzdGVyIn0.f8L7Mg3aXUMcXU5I1jGpqJh7ORYuOGrtZtLHL4ZusiY"

DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"
YELLOW = "\033[33m"


def make_token(user_id: int) -> str:
    """--token 미지정 시에만 사용 — gw 레포·.env(DJANGO_SECRET) 필요."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    try:
        from jose import jwt

        from src.config import settings
    except ImportError:
        sys.exit("토큰 자동 서명은 gw 레포 안에서만 가능합니다. --token <JWT> 로 직접 지정하세요.")
    return jwt.encode(
        {"user_id": user_id, "username": "chat-repl"},
        settings.DJANGO_SECRET,
        algorithm=settings.ALGORITHM,
    )


def info(text: str) -> None:
    print(f"{DIM}{text}{RESET}")


class ChatSession:
    def __init__(self, base_url: str, token: str) -> None:
        self.client = httpx.Client(base_url=base_url, timeout=httpx.Timeout(10.0, read=None))
        self.headers = {"Authorization": f"Bearer {token}"}
        self.conversation_id: str | None = None
        self.claim_id: int | None = None
        self.document_id: int | None = None

    def send(self, message: str) -> None:
        body: dict = {"message": message}
        if self.conversation_id:
            body["conversation_id"] = self.conversation_id
        if self.claim_id is not None:
            body["claim_id"] = self.claim_id
        if self.document_id is not None:
            body["document_id"] = self.document_id

        try:
            with self.client.stream("POST", "/api/v1/chat", json=body, headers=self.headers) as resp:
                if resp.status_code != 200:
                    resp.read()
                    print(f"{YELLOW}HTTP {resp.status_code}: {resp.text}{RESET}")
                    return
                self._consume_sse(resp)
        except KeyboardInterrupt:
            # 연결만 끊고 REPL 유지 — 서버는 partial-save(stopped_by_user) 해야 한다
            print(f"\n{YELLOW}[중단됨 — DB 에 stopped_by_user=true 로 저장됐는지 확인]{RESET}")
        except httpx.ConnectError:
            print(f"{YELLOW}서버에 연결할 수 없습니다. uvicorn 이 떠 있는지 확인하세요.{RESET}")
        except (httpx.RemoteProtocolError, httpx.ReadError):
            print(
                f"\n{YELLOW}[연결이 비정상 종료됨 — 서버 로그 확인. 응답은 partial-save 로 보존됩니다]{RESET}"
            )

    def _consume_sse(self, resp: httpx.Response) -> None:
        event = ""
        for line in resp.iter_lines():
            if line.startswith("event: "):
                event = line[len("event: ") :]
            elif line.startswith("data: "):
                self._handle(event, json.loads(line[len("data: ") :]))

    def _handle(self, event: str, data: dict) -> None:
        if event == "conversation":
            if self.conversation_id is None:
                info(f"[대화 시작 conversation_id={data['conversation_id']}]")
            self.conversation_id = data["conversation_id"]
        elif event == "token":
            print(data.get("text", ""), end="", flush=True)
        elif event == "stage_started":
            print(f"\n{DIM}[{data.get('name', '')} 실행 중...]{RESET}", flush=True)
        elif event == "stage_completed":
            info(f"[{data.get('name', '')} 완료]")
        elif event == "error":
            print(f"\n{YELLOW}[error] {data}{RESET}")
        elif event == "done":
            reason = data.get("finish_reason", "stop")
            suffix = "" if reason == "stop" else f" (finish_reason={reason})"
            print(f"\n{DIM}[완료{suffix}]{RESET}")


def handle_command(session: ChatSession, line: str) -> bool:
    """REPL 명령 처리. 종료면 False 반환."""
    cmd, *rest = line.split(maxsplit=1)
    arg = rest[0] if rest else None

    if cmd == "/quit":
        return False
    if cmd == "/new":
        session.conversation_id = None
        info("[새 대화]")
    elif cmd == "/claim":
        session.claim_id = int(arg) if arg else None
        info(f"[claim_id={session.claim_id}]")
    elif cmd == "/doc":
        session.document_id = int(arg) if arg else None
        info(f"[document_id={session.document_id}]")
    else:
        info("명령: /new /claim N /doc N /quit")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="gw 채팅 SSE 수동 테스트 REPL")
    parser.add_argument("--user-id", type=int, default=2, help="JWT user_id (기본 2 — dev 테스트 계정)")
    parser.add_argument("--base-url", default="https://data-dev.patsol.kr")
    parser.add_argument("--token", default=None, help="직접 발급한 JWT 사용 (생략 시 자동 서명)")
    args = parser.parse_args()

    token = args.token or DEFAULT_TOKEN or make_token(args.user_id)
    session = ChatSession(args.base_url, token)

    print(f"{BOLD}gw 채팅 테스트 REPL{RESET} — {args.base_url} / user_id={args.user_id}")
    info("명령: /new /claim N /doc N /quit  (로컬 서버 테스트: --base-url http://localhost:8003)")

    while True:
        try:
            line = input(f"\n{BOLD}> {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line.startswith("/"):
            if not handle_command(session, line):
                break
            continue
        session.send(line)


if __name__ == "__main__":
    main()

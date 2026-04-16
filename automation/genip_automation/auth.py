"""
auth.py — genip.app 로그인 처리 및 세션 저장
"""

import json
import os
from pathlib import Path
from playwright.sync_api import Page, BrowserContext

SESSION_FILE = Path(__file__).parent / "output" / "session.json"
LOGIN_URL = "https://genip.app/login"


def login(page: Page, email: str, password: str) -> bool:
    """이메일/비밀번호로 로그인하고 성공 여부 반환."""
    from pathlib import Path as _Path

    print(f"[auth] {LOGIN_URL} 접속 중...")
    page.goto(LOGIN_URL, wait_until="networkidle")

    # 입력 필드가 DOM에 나타날 때까지 대기 (최대 15초)
    page.wait_for_selector("input", state="visible", timeout=15000)

    # 디버그: 현재 페이지 입력 필드 목록 출력
    inputs = page.locator("input").all()
    print(f"[auth] 발견된 input 요소: {len(inputs)}개")
    for i, inp in enumerate(inputs):
        try:
            t = inp.get_attribute("type") or "-"
            n = inp.get_attribute("name") or "-"
            ph = inp.get_attribute("placeholder") or "-"
            print(f"       [{i}] type={t} name={n} placeholder={ph}")
        except Exception:
            pass

    # 이메일 입력 — 가장 첫 번째 text/email 입력 필드 사용
    try:
        email_input = page.locator("input[type='email']").first
        email_input.wait_for(state="visible", timeout=5000)
    except Exception:
        try:
            email_input = page.locator("input[type='text']").first
            email_input.wait_for(state="visible", timeout=5000)
        except Exception:
            email_input = page.locator("input").first
            email_input.wait_for(state="visible", timeout=5000)
    email_input.click()
    email_input.press_sequentially(email, delay=50)

    # 비밀번호 입력
    password_input = page.locator("input[type='password']").first
    password_input.wait_for(state="visible", timeout=5000)
    password_input.click()
    password_input.press_sequentially(password, delay=50)

    # 로그인 버튼 클릭
    buttons = page.locator("button").all()
    print(f"[auth] 발견된 button 요소: {len(buttons)}개")
    for i, btn in enumerate(buttons):
        try:
            print(f"       [{i}] text='{btn.inner_text(timeout=1000).strip()}'")
        except Exception:
            pass

    submit_btn = page.locator("button:has-text('로그인')").first
    submit_btn.click()

    # 클릭 직후 잠시 대기 후 중간 스크린샷
    page.wait_for_timeout(3000)
    mid_path = _Path(__file__).parent / "output" / "login_after_click.png"
    mid_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(mid_path))
    print(f"[auth] 클릭 후 스크린샷: {mid_path} (현재 URL: {page.url})")

    # 로그인 완료 대기 — /login URL에서 벗어나면 성공
    try:
        page.wait_for_url(lambda url: "/login" not in url, timeout=15000)
        print(f"[auth] 로그인 성공. 현재 URL: {page.url}")
        return True
    except Exception:
        screenshot_path = _Path(__file__).parent / "output" / "login_failed.png"
        page.screenshot(path=str(screenshot_path))
        print(f"[auth] 로그인 실패. 스크린샷 저장: {screenshot_path}")
        return False


def save_session(context: BrowserContext) -> None:
    """현재 브라우저 세션(쿠키 + 스토리지)을 파일로 저장."""
    SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    storage = context.storage_state()
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(storage, f, ensure_ascii=False, indent=2)
    print(f"[auth] 세션 저장: {SESSION_FILE}")


def load_session(context: BrowserContext) -> bool:
    """저장된 세션이 있으면 로드. 없으면 False 반환."""
    if not SESSION_FILE.exists():
        return False
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        storage = json.load(f)
    context.add_cookies(storage.get("cookies", []))
    print(f"[auth] 세션 로드: {SESSION_FILE}")
    return True

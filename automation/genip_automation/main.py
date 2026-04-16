"""
main.py — GenIP 자동화 진입점

사용법:
  python main.py --task features   # 기능 명세서 추출
  python main.py --task prompts    # LLM 프롬프트 스니핑
  python main.py --task all        # 두 작업 동시 실행

환경 변수 (.env 또는 직접 설정):
  GENIP_EMAIL     로그인 이메일
  GENIP_PASSWORD  로그인 비밀번호
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

import auth
import feature_map
import prompt_sniffer

load_dotenv(Path(__file__).parent / ".env")

BASE_URL = "https://genip.app"


def get_credentials() -> tuple[str, str]:
    user_id = os.environ.get("GENIP_ID", "") or os.environ.get("GENIP_EMAIL", "")
    password = os.environ.get("GENIP_PASSWORD", "")
    if not user_id:
        user_id = input("GENIP 아이디: ").strip()
    if not password:
        import getpass
        password = getpass.getpass("GENIP 비밀번호: ")
    return user_id, password


def run_features(headless: bool = False) -> None:
    email, password = get_credentials()
    feature_map._visited.clear()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()

        # 저장된 세션 로드 시도
        if not auth.load_session(context):
            page = context.new_page()
            if not auth.login(page, email, password):
                print("[main] 로그인 실패. 종료합니다.")
                browser.close()
                sys.exit(1)
            auth.save_session(context)
        else:
            page = context.new_page()
            page.goto(BASE_URL, wait_until="networkidle")
            # 세션 만료 확인
            if "login" in page.url:
                print("[main] 저장된 세션 만료. 재로그인 중...")
                if not auth.login(page, email, password):
                    print("[main] 로그인 실패. 종료합니다.")
                    browser.close()
                    sys.exit(1)
                auth.save_session(context)

        print(f"\n[main] 기능 명세 추출 시작 (시작 URL: {page.url})")
        items = feature_map.extract_features(page, depth=0, max_depth=3)

        feature_map.save_csv(items)
        feature_map.save_markdown(items)

        print(f"\n[main] 완료: {len(items)}개 기능 항목 추출")
        browser.close()


def run_prompts(headless: bool = False) -> None:
    email, password = get_credentials()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()

        if not auth.load_session(context):
            page = context.new_page()
            if not auth.login(page, email, password):
                print("[main] 로그인 실패. 종료합니다.")
                browser.close()
                sys.exit(1)
            auth.save_session(context)
        else:
            page = context.new_page()
            page.goto(BASE_URL, wait_until="networkidle")
            if "login" in page.url:
                if not auth.login(page, email, password):
                    print("[main] 로그인 실패. 종료합니다.")
                    browser.close()
                    sys.exit(1)
                auth.save_session(context)

        # 네트워크 인터셉트 활성화
        prompt_sniffer.attach(page)

        print("\n[main] LLM 프롬프트 스니핑 모드 시작")
        print("       브라우저에서 GenIP 기능을 직접 사용하세요.")
        print("       종료하려면 Enter를 누르세요...\n")

        try:
            input()  # 사용자가 직접 기능 탐색
        except KeyboardInterrupt:
            pass

        prompt_sniffer.print_summary()
        browser.close()


def run_all(headless: bool = False) -> None:
    """features와 prompts를 순차 실행."""
    print("=== Task 1: 기능 명세 추출 ===")
    run_features(headless=headless)
    print("\n=== Task 2: LLM 프롬프트 스니핑 ===")
    run_prompts(headless=headless)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GenIP 자동화 도구")
    parser.add_argument(
        "--task",
        choices=["features", "prompts", "all"],
        default="features",
        help="실행할 작업 (기본값: features)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="헤드리스 모드로 실행 (브라우저 창 숨김)",
    )
    args = parser.parse_args()

    if args.task == "features":
        run_features(headless=args.headless)
    elif args.task == "prompts":
        run_prompts(headless=args.headless)
    else:
        run_all(headless=args.headless)

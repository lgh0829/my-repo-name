"""
feature_map.py — Task 1: 버튼/링크 순회 및 기능 명세 추출
"""

import csv
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from urllib.parse import urlparse, urljoin
from playwright.sync_api import Page

OUTPUT_CSV = Path(__file__).parent / "output" / "features.csv"
OUTPUT_MD = Path(__file__).parent / "output" / "features.md"
BASE_URL = "https://genip.app"

# 방문 방지용 블랙리스트 (실제 기능을 트리거하지 않을 레이블)
SKIP_LABELS = {
    "delete", "삭제", "remove", "제거", "logout", "로그아웃",
    "submit", "저장", "save", "publish", "배포",
}

# 이미 방문한 URL 추적
_visited: set[str] = set()


@dataclass
class FeatureItem:
    page_title: str
    url: str
    element_type: str      # button | link | form
    label: str
    description: str
    input_fields: str      # 쉼표로 구분된 입력 필드명


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def _is_internal(url: str) -> bool:
    return url.startswith(BASE_URL) or url.startswith("/")


def _safe_text(page: Page, selector: str) -> str:
    try:
        el = page.locator(selector).first
        return el.inner_text(timeout=2000).strip()
    except Exception:
        return ""


def _get_page_description(page: Page) -> str:
    """h1, h2, meta[description] 등에서 현재 페이지 설명 추출."""
    for sel in ["h1", "h2", "meta[name='description']"]:
        text = _safe_text(page, sel)
        if text:
            return text[:200]
    return ""


def _get_input_fields(page: Page) -> str:
    """현재 페이지의 입력 필드 레이블/placeholder 목록 반환."""
    fields = []
    for inp in page.locator("input:not([type='hidden']), textarea, select").all():
        try:
            name = inp.get_attribute("placeholder") or inp.get_attribute("name") or inp.get_attribute("aria-label") or ""
            if name:
                fields.append(name.strip())
        except Exception:
            pass
    return ", ".join(dict.fromkeys(fields))  # 중복 제거, 순서 유지


def extract_features(page: Page, depth: int = 0, max_depth: int = 3) -> list[FeatureItem]:
    """현재 페이지의 버튼/링크를 순회하며 기능 명세 수집."""
    if depth > max_depth:
        return []

    current_url = _normalize_url(page.url)
    if current_url in _visited:
        return []
    _visited.add(current_url)

    results: list[FeatureItem] = []
    page_title = page.title() or _get_page_description(page)

    print(f"[feature_map] {'  ' * depth}📄 {page_title} ({current_url})")

    # ── 현재 페이지 입력 필드 기록 ──────────────────────────────
    input_fields = _get_input_fields(page)

    # ── 버튼 수집 ────────────────────────────────────────────────
    buttons = page.locator("button:visible, [role='button']:visible").all()
    for btn in buttons:
        try:
            label = (btn.inner_text(timeout=1000) or btn.get_attribute("aria-label") or "").strip()
            if not label or label.lower() in SKIP_LABELS:
                continue
            results.append(FeatureItem(
                page_title=page_title,
                url=current_url,
                element_type="button",
                label=label,
                description=_get_page_description(page),
                input_fields=input_fields,
            ))
        except Exception:
            pass

    # ── 링크 수집 및 재귀 ────────────────────────────────────────
    links = page.locator("a[href]:visible").all()
    for link in links:
        try:
            href = link.get_attribute("href") or ""
            label = (link.inner_text(timeout=1000) or link.get_attribute("aria-label") or "").strip()

            if not href or href.startswith("#") or not _is_internal(href):
                continue
            if label.lower() in SKIP_LABELS:
                continue

            abs_url = urljoin(BASE_URL, href)
            norm_url = _normalize_url(abs_url)

            results.append(FeatureItem(
                page_title=page_title,
                url=current_url,
                element_type="link",
                label=label,
                description=_get_page_description(page),
                input_fields=input_fields,
            ))

            if norm_url not in _visited and depth < max_depth:
                print(f"[feature_map] {'  ' * depth}  → {label} ({abs_url})")
                page.goto(abs_url, wait_until="networkidle", timeout=15000)
                child_results = extract_features(page, depth + 1, max_depth)
                results.extend(child_results)
                page.go_back(wait_until="networkidle", timeout=10000)

        except Exception as e:
            print(f"[feature_map] 링크 처리 오류: {e}")
            continue

    return results


def save_csv(items: list[FeatureItem]) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(FeatureItem.__dataclass_fields__.keys()))
        writer.writeheader()
        writer.writerows([asdict(item) for item in items])
    print(f"[feature_map] CSV 저장: {OUTPUT_CSV} ({len(items)}건)")


def save_markdown(items: list[FeatureItem]) -> None:
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# GenIP 기능 명세서\n"]

    # 페이지 단위로 그룹화
    pages: dict[str, list[FeatureItem]] = {}
    for item in items:
        pages.setdefault(item.page_title, []).append(item)

    for page_title, page_items in pages.items():
        lines.append(f"\n## {page_title}\n")
        lines.append(f"**URL:** {page_items[0].url}\n")
        if page_items[0].description:
            lines.append(f"**설명:** {page_items[0].description}\n")
        if page_items[0].input_fields:
            lines.append(f"**입력 필드:** {page_items[0].input_fields}\n")
        lines.append("\n| 유형 | 레이블 |\n|------|--------|\n")
        seen = set()
        for item in page_items:
            key = (item.element_type, item.label)
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"| {item.element_type} | {item.label} |\n")

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"[feature_map] Markdown 저장: {OUTPUT_MD}")

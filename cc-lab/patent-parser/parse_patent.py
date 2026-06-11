#!/usr/bin/env python3
"""
parse_patent.py — 특허 명세서 docx를 도면 평가 에이전트용 구조화 Markdown으로 변환.

사용법:
    python3 parse_patent.py <input.docx> [output.md]
    python3 parse_patent.py <input.docx>   # → <input>_parsed.md 로 저장

지원 헤더 형식:
    영문: 【Title of Invention】, 【Claims 1】, 【Brief Description of Drawings】, ...
    한글: 【발명의 명칭】, 【청구항 1】, 【도면의 간단한 설명】, ...
"""

import re
import sys
from pathlib import Path
from docx import Document


# ── 참조번호 패턴: (10), (11A), (20-1), (11A-1), (21A'), (S1) 등
REF_PATTERN = re.compile(r"\(([A-Za-z]?\d+[A-Z]?(?:-\d+[A-Z]?)?'?)\)")

# ── 헤더 패턴: 【...】
HEADER_PATTERN = re.compile(r"^【(.+?)】\s*$")

# ── 청구항 번호 헤더: "Claims 1", "청구항 1" 등
CLAIM_ITEM_PATTERN = re.compile(
    r"^(?:Claims?\s+(\d+)|청구항\s*(\d+))$", re.IGNORECASE
)

# ── 섹션 헤더 키워드 → 내부 키 매핑 (영문/한글 모두 지원)
SECTION_KEYWORDS = [
    # (포함 문자열,                           내부 키)
    ("Title of Invention",                   "title"),
    ("발명의 명칭",                           "title"),
    ("Brief Description of Drawings",        "drawings"),
    ("도면의 간단한 설명",                    "drawings"),
    ("Specific Contents to Carry Out",       "description"),
    ("발명을 실시하기 위한 구체적인 내용",     "description"),
    ("발명을 실시하기 위한",                  "description"),
    ("구체적인 내용",                         "description"),
    ("Reference Signs",                      "ref_signs"),
    ("부호의 설명",                           "ref_signs"),
    ("Means to Solve",                       "means"),
    ("과제의 해결 수단",                      "means"),
    # 청구범위 섹션 시작
    ("Claim",                                "claims_section"),
    ("청구범위",                             "claims_section"),
    # 무시 헤더
    ("Description of Invention",            "_ignore"),
    ("발명의 설명",                          "_ignore"),
    ("Technical Field",                     "_ignore"),
    ("기술 분야",                            "_ignore"),
    ("Background Technology",               "_ignore"),
    ("배경기술",                             "_ignore"),
    ("Contents of Invention",               "_ignore"),
    ("발명의 내용",                          "_ignore"),
    ("Problems to Solve",                   "_ignore"),
    ("해결하려는 과제",                       "_ignore"),
    ("Effects of the Invention",            "_ignore"),
    ("발명의 효과",                          "_ignore"),
    ("Summary",                             "_ignore"),
    ("요약",                                "_ignore"),
    ("요약서",                              "_ignore"),
]


def classify_header(header_text):
    """
    【...】 내부 텍스트를 받아 (section_key, claim_num) 반환.
    - 청구항 헤더: ('claim_item', N)
    - 섹션 헤더:   (key, None)
    - 미인식:      (None, None)
    """
    text = header_text.strip()

    # 청구항 개별 헤더 먼저 확인
    m = CLAIM_ITEM_PATTERN.match(text)
    if m:
        num = int(m.group(1) or m.group(2))
        return "claim_item", num

    # 섹션 키워드 매칭
    for keyword, key in SECTION_KEYWORDS:
        if keyword in text:
            return key, None

    return None, None


def parse_docx(path):
    """docx를 읽어 구조화된 딕셔너리로 반환."""
    doc = Document(path)

    result = {
        "title": "",
        "claims": [],       # [{"num": 1, "text": "..."}, ...]
        "description": [],  # [str, ...]
        "drawings": [],     # [str, ...]
        "ref_signs": [],    # [str, ...]
        "means": [],        # 과제 해결 수단 (청구항 보조 텍스트)
    }

    current_section = None
    current_claim_num = None
    current_claim_lines = []

    def flush_claim():
        if current_claim_num is not None and current_claim_lines:
            result["claims"].append({
                "num": current_claim_num,
                "text": " ".join(current_claim_lines).strip(),
            })

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        hm = HEADER_PATTERN.match(text)
        if hm:
            flush_claim()
            current_claim_num = None
            current_claim_lines = []

            key, claim_num = classify_header(hm.group(1))

            if key == "claim_item":
                current_section = "claims_section"
                current_claim_num = claim_num
            elif key == "_ignore" or key is None:
                current_section = None
            else:
                current_section = key
            continue

        # 본문 수집
        if current_claim_num is not None:
            current_claim_lines.append(text)
        elif current_section == "title":
            if not result["title"]:
                result["title"] = text
        elif current_section in ("description", "means", "drawings", "ref_signs"):
            result[current_section].append(text)

    flush_claim()
    return result


# ── 참조번호/도면 추출 유틸리티 ─────────────────────────────────────


def extract_ref_numbers(text):
    """텍스트에서 참조번호 목록 추출 (중복 제거, 숫자 기준 정렬)."""
    refs = REF_PATTERN.findall(text)

    def sort_key(r):
        m = re.match(r"[A-Za-z]*(\d+)", r)
        return (int(m.group(1)) if m else 9999, r)

    return sorted(set(refs), key=sort_key)


def parse_ref_sign_section(raw_lines):
    """부호의 설명 섹션에서 '참조번호 : 명칭' 행을 파싱."""
    entries = []
    pattern = re.compile(
        r"^\(?([A-Za-z]?\d+[A-Z]?(?:-\d+[A-Z]?)?'?)\)?"
        r"[\s:：.\-–—]+"
        r"(.+)$"
    )
    for line in raw_lines:
        m = pattern.match(line.strip())
        if m:
            entries.append({"ref": m.group(1), "name": m.group(2).strip()})
    return entries


def build_ref_map(claims, description_lines, means_lines, ref_sign_entries):
    """참조번호 → 명칭 맵 구축."""
    ref_map = {}

    # 1) 부호의 설명 (최우선)
    for e in ref_sign_entries:
        ref_map[e["ref"]] = e["name"]

    # 2) 본문에서 "명칭(번호)" 역방향 패턴 추출
    reverse_pattern = re.compile(
        r"([가-힣a-zA-Z][가-힣a-zA-Z\s]{1,15}?)\s*"
        r"\(([A-Za-z]?\d+[A-Z]?(?:-\d+[A-Z]?)?'?)\)"
        r"(?!\s*\(\d)"
    )
    for line in description_lines + means_lines:
        for m in reverse_pattern.finditer(line):
            name_raw, ref = m.group(1).strip(), m.group(2)
            name = re.sub(r"^(?:및|또는|상기|the|a|an)\s+", "", name_raw).strip()
            if ref not in ref_map and len(name) >= 2:
                ref_map[ref] = name

    # 3) 청구항에 등장하지만 이름 없는 번호 → "—"
    all_claim_text = " ".join(c["text"] for c in claims)
    for ref in extract_ref_numbers(all_claim_text):
        if ref not in ref_map:
            ref_map[ref] = "—"

    return ref_map


def extract_figure_descriptions(raw_lines):
    """'도 N', '[도 N]' 패턴으로 도면 설명을 분리."""
    figures = []
    current_fig = None
    current_lines = []

    fig_pattern = re.compile(
        r"^(?:\[?도\s*(\d+)(?:[은는이가의을를]?)[\].\s:：—\-]?)(.*)"
    )

    for line in raw_lines:
        m = fig_pattern.match(line)
        if m:
            if current_fig is not None:
                figures.append({
                    "id": current_fig,
                    "description": " ".join(current_lines).strip(),
                })
            current_fig = m.group(1)
            rest = m.group(2).strip()
            current_lines = [rest] if rest else []
        else:
            if current_fig is not None:
                current_lines.append(line)

    if current_fig is not None:
        figures.append({
            "id": current_fig,
            "description": " ".join(current_lines).strip(),
        })

    return figures


def ref_sort_key(r):
    m = re.match(r"[A-Za-z]*(\d+)", r)
    return (int(m.group(1)) if m else 9999, r)


def render_checklist(claims, figures, ref_map):
    """도면별 검토 체크리스트 마크다운 생성."""
    lines = ["## 5. 도면별 검토 체크리스트\n"]
    lines.append("> 이 체크리스트는 `patent-figure-reviewer` 에이전트가 직접 사용합니다.\n")

    if not figures:
        lines.append("### 전체 도면 공통 체크리스트\n")
        lines.append("*(도면의 간단한 설명 섹션이 감지되지 않아 청구항 기반으로 생성)*\n")
        for ref in sorted(ref_map.keys(), key=ref_sort_key):
            lines.append(f"- [ ] ({ref}) {ref_map.get(ref, '—')}")
        return "\n".join(lines)

    for fig in figures:
        fig_id = fig["id"]
        desc = fig["description"]
        lines.append(f"### 도 {fig_id}")
        if desc:
            lines.append(f"> {desc}\n")

        fig_text = desc
        for claim in claims:
            if f"도 {fig_id}" in claim["text"] or f"도{fig_id}" in claim["text"]:
                fig_text += " " + claim["text"]

        fig_refs = extract_ref_numbers(fig_text)
        target_refs = fig_refs if fig_refs else list(ref_map.keys())

        for ref in sorted(target_refs, key=ref_sort_key):
            lines.append(f"- [ ] ({ref}) {ref_map.get(ref, '—')}")
        lines.append("")

    return "\n".join(lines)


def render_markdown(path, data):
    """파싱 결과를 에이전트 친화적 마크다운으로 렌더링."""
    claims = data["claims"]
    figures = extract_figure_descriptions(data["drawings"])
    ref_sign_entries = parse_ref_sign_section(data["ref_signs"])
    ref_map = build_ref_map(claims, data["description"], data["means"], ref_sign_entries)

    title = data["title"] or path.stem
    out = []

    out.append(f"# 특허 명세서 구조화 — {title}")
    out.append(f"> 파싱 대상: `{path.name}`\n")
    out.append("---\n")

    # 1. 발명의 명칭
    out.append("## 1. 발명의 명칭\n")
    out.append(title + "\n")

    # 2. 청구항
    out.append("## 2. 청구항 (Claims)\n")
    if claims:
        for c in claims:
            out.append(f"### 청구항 {c['num']}\n")
            out.append(c["text"] + "\n")
    else:
        out.append("*(청구항 섹션을 감지하지 못했습니다)*\n")

    # 3. 구성요소 참조번호 목록
    out.append("## 3. 구성요소 참조번호 목록\n")
    out.append("| 참조번호 | 구성요소명 | 출처 |")
    out.append("|:---:|:---|:---:|")
    ref_sign_set = {e["ref"] for e in ref_sign_entries}
    for ref, name in sorted(ref_map.items(), key=lambda x: ref_sort_key(x[0])):
        source = "부호설명" if ref in ref_sign_set else "추출"
        out.append(f"| ({ref}) | {name} | {source} |")
    out.append("")

    # 4. 도면의 간단한 설명
    out.append("## 4. 도면의 간단한 설명\n")
    if figures:
        for fig in figures:
            out.append(f"### 도 {fig['id']}")
            out.append(fig["description"] + "\n")
    elif data["drawings"]:
        out.append("\n".join(data["drawings"]) + "\n")
    else:
        out.append("*(도면 설명 섹션을 감지하지 못했습니다)*\n")

    # 5. 도면별 검토 체크리스트
    out.append(render_checklist(claims, figures, ref_map))

    # 6. 부호의 설명 원문
    if data["ref_signs"]:
        out.append("## 6. 부호의 설명 (원문)\n")
        for line in data["ref_signs"]:
            out.append(line)
        out.append("")

    # 7. 청구항 전문
    out.append("## 7. 청구항 전문 (에이전트 참조용)\n")
    out.append("```text")
    for c in claims:
        out.append(f"[청구항 {c['num']}]")
        out.append(c["text"])
        out.append("")
    out.append("```")

    return "\n".join(out)


def main():
    import shutil

    if len(sys.argv) < 2:
        print("사용법: python3 parse_patent.py <input.docx> [output.md]")
        sys.exit(1)

    input_path = Path(sys.argv[1]).resolve()
    if not input_path.exists():
        print(f"파일을 찾을 수 없습니다: {input_path}")
        sys.exit(1)

    # 현재 디렉토리 기준 output/ 폴더
    output_dir = Path.cwd() / "output"
    output_dir.mkdir(exist_ok=True)

    # 외부 경로 docx → output/ 으로 복사
    dest_docx = output_dir / input_path.name
    if input_path != dest_docx:
        shutil.copy2(input_path, dest_docx)
        print(f"복사: {input_path.name} → output/")

    # 파싱 결과도 output/ 에 저장
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = output_dir / (input_path.stem + "_parsed.md")

    print(f"파싱 중: {input_path.name}")
    data = parse_docx(input_path)
    md = render_markdown(input_path, data)

    output_path.write_text(md, encoding="utf-8")
    print(f"완료: {output_path}")

    print("\n── 섹션 감지 현황 ──")
    print(f"  {'title':15s}: {'✓' if data['title'] else '✗ (감지 실패)'}")
    for key in ("claims", "description", "drawings", "ref_signs"):
        count = len(data[key])
        status = f"{count:3d}줄  ✓" if count > 0 else "  0줄  ✗ (감지 실패)"
        print(f"  {key:15s}: {status}")
    print(f"  {'means(보조)':15s}: {len(data['means']):3d}줄")


if __name__ == "__main__":
    main()

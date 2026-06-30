"""
Phase 2 — raw JSON → MD / PDF / JSON 세 포맷 변환
대상 디렉토리를 --source 로 지정:
  python scripts/convert.py --source sample   # data-sample/raw → data-sample/{md,pdf,json}
  python scripts/convert.py --source all      # data-all/raw_all → data-all/{md,pdf,json}
"""

import json
import argparse
import re
from pathlib import Path

from fpdf import FPDF

# ── 경로 상수 ──────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).parent.parent
FONT_PATH  = ROOT / "NanumGothic.ttf"

SOURCE_MAP = {
    "sample": {
        "raw": ROOT / "data-sample" / "raw",
        "md":  ROOT / "data-sample" / "md",
        "pdf": ROOT / "data-sample" / "pdf",
        "json": ROOT / "data-sample" / "json",
    },
    "all": {
        "raw": ROOT / "data-all" / "raw",
        "md":  ROOT / "data-all" / "md",
        "pdf": ROOT / "data-all" / "pdf",
        "json": ROOT / "data-all" / "json",
    },
}

# ── 명세서 섹션 정의 (필드 → 한글 헤더) ─────────────────────────────────────
SECTIONS = [
    ("TechnicalField",          "기술분야"),
    ("Background",              "배경기술"),
    ("Problem",                 "해결하려는 과제"),
    ("SolutionProblem",         "과제의 해결 수단"),
    ("Effects",                 "발명의 효과"),
    ("BriefDescriptionOfDrawings", "도면의 간단한 설명"),
    ("Embodiment",              "발명을 실시하기 위한 구체적인 내용"),
    ("Claims",                  "청구항"),
    ("Abstract",                "요약"),
    ("Summary",                 "요약서"),
]

META_FIELDS = ["ApplicationNumber", "Title", "MainCPC", "SubCPC",
               "ApplicationDate", "ApplicantName", "AgentNames"]


def clean_text(text: str) -> str:
    """단락 구분자 정규화, HTML 태그 제거, 연속 공백 정리"""
    if not text:
        return ""
    text = text.replace("¶", "\n")
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ── MD 변환 ───────────────────────────────────────────────────────────────────
def to_md(doc: dict) -> str:
    lines = []
    title = doc.get("Title", "제목 없음")
    app_num = doc.get("ApplicationNumber", "")
    lines.append(f"# {title}")
    lines.append(f"\n**출원번호**: {app_num}  ")
    lines.append(f"**CPC**: {doc.get('MainCPC', '')}  ")
    lines.append(f"**출원일**: {doc.get('ApplicationDate', '')}  ")
    lines.append(f"**출원인**: {doc.get('ApplicantName', '')}  ")
    lines.append("")

    for field, header in SECTIONS:
        text = clean_text(doc.get(field, ""))
        if text:
            lines.append(f"## {header}")
            lines.append("")
            lines.append(text)
            lines.append("")

    return "\n".join(lines)


# ── JSON 변환 ─────────────────────────────────────────────────────────────────
def to_json(doc: dict) -> dict:
    meta = {f: doc.get(f, "") for f in META_FIELDS}
    sections = []
    for field, header in SECTIONS:
        text = clean_text(doc.get(field, ""))
        if text:
            sections.append({"section": header, "field": field, "text": text})
    return {"meta": meta, "sections": sections}


# ── PDF 변환 ──────────────────────────────────────────────────────────────────
class KoreanPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Nanum", "", str(FONT_PATH))
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        pass

    def write_title(self, text: str):
        self.set_font("Nanum", size=14)
        self.multi_cell(0, 8, text)
        self.ln(2)

    def write_section(self, header: str, body: str):
        self.set_font("Nanum", size=11)
        self.set_fill_color(230, 230, 230)
        from fpdf.enums import XPos, YPos
        self.cell(0, 7, f"  {header}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(1)
        self.set_font("Nanum", size=9)
        self.multi_cell(0, 5, body)
        self.ln(3)


def to_pdf(doc: dict, out_path: Path):
    pdf = KoreanPDF()
    pdf.add_page()

    title = doc.get("Title", "제목 없음")
    app_num = doc.get("ApplicationNumber", "")
    meta_line = (
        f"출원번호: {app_num}  |  CPC: {doc.get('MainCPC','')}  |  "
        f"출원일: {doc.get('ApplicationDate','')}  |  출원인: {doc.get('ApplicantName','')}"
    )
    pdf.write_title(title)
    pdf.set_font("Nanum", size=8)
    pdf.multi_cell(0, 5, meta_line)
    pdf.ln(4)

    for field, header in SECTIONS:
        text = clean_text(doc.get(field, ""))
        if text:
            pdf.write_section(header, text)

    pdf.output(str(out_path))


# ── 메인 ──────────────────────────────────────────────────────────────────────
def convert_one(raw_path: Path, dirs: dict, resume: bool):
    app_num = raw_path.stem
    md_path   = dirs["md"]   / f"{app_num}.md"
    pdf_path  = dirs["pdf"]  / f"{app_num}.pdf"
    json_path = dirs["json"] / f"{app_num}.json"

    if resume and md_path.exists() and pdf_path.exists() and json_path.exists():
        return "skip"

    doc = json.loads(raw_path.read_text(encoding="utf-8"))

    if not md_path.exists() or not resume:
        md_path.write_text(to_md(doc), encoding="utf-8")

    if not json_path.exists() or not resume:
        json_path.write_text(
            json.dumps(to_json(doc), ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if not pdf_path.exists() or not resume:
        to_pdf(doc, pdf_path)

    return "ok"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["sample", "all"], default="sample")
    parser.add_argument("--resume", action="store_true", help="이미 변환된 파일 건너뜀")
    args = parser.parse_args()

    dirs = SOURCE_MAP[args.source]
    for d in ("md", "pdf", "json"):
        dirs[d].mkdir(parents=True, exist_ok=True)

    raw_files = sorted(dirs["raw"].glob("*.json"))
    total = len(raw_files)
    print(f"[{args.source}] 변환 대상: {total}건")

    ok = skip = fail = 0
    for i, raw_path in enumerate(raw_files, 1):
        try:
            result = convert_one(raw_path, dirs, args.resume)
            if result == "skip":
                skip += 1
            else:
                ok += 1
                if i % 200 == 0 or i == total:
                    print(f"  [{i}/{total}] {raw_path.stem}")
        except Exception as e:
            print(f"  [ERR] {raw_path.stem}: {e}")
            fail += 1

    print(f"\n완료 — 성공: {ok}, 스킵: {skip}, 오류: {fail}")
    print(f"  MD  → {dirs['md']}")
    print(f"  PDF → {dirs['pdf']}")
    print(f"  JSON→ {dirs['json']}")


if __name__ == "__main__":
    main()

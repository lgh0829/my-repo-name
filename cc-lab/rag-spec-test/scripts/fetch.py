"""
Phase 1 — ES v1에서 명세서 수집 → data/raw/<출원번호>.json
CPC 대분류별 균등 샘플링 (기본 30건, --count로 조정)
"""

import csv
import json
import os
import random
import argparse
from pathlib import Path
from collections import defaultdict

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

# ── ES v1 접속 정보 ────────────────────────────────────────────────────────────
ES_URL      = "http://192.168.0.163:9204"
ES_USERNAME = "elastic"
ES_PASSWORD = "Rx6U8blh53KmWzs1Brnj"
ES_INDEX    = "kr_pub_patents"

# ── 수집할 필드 (InventorName 제외) ────────────────────────────────────────────
FIELDS = [
    "ApplicationNumber", "Title", "MainCPC", "SubCPC",
    "ApplicationDate", "ApplicantName", "AgentNames",
    "Abstract", "Claims", "TechnicalField", "Background",
    "Problem", "SolutionProblem", "Effects",
    "BriefDescriptionOfDrawings", "Embodiment", "Summary",
]

LIST_CSV  = Path("/Users/leegh/cc-workspace/es-search/output/list.csv")
RAW_DIR   = Path(__file__).parent.parent / "data-sample" / "raw"


def load_app_numbers():
    """list.csv에서 (출원번호, CPC대분류) 목록 반환"""
    rows = []
    with open(LIST_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            app_num = row.get("출원번호", "").strip()
            cpc     = row.get("MainCPC", "").strip()[:4]  # 대분류 4자리
            if app_num:
                rows.append((app_num, cpc))
    return rows


def sample_by_cpc(rows, total=30):
    """CPC 대분류별 균등 샘플링"""
    by_cpc = defaultdict(list)
    for app_num, cpc in rows:
        by_cpc[cpc].append(app_num)

    groups   = list(by_cpc.keys())
    per_group = max(1, total // len(groups))

    sampled = []
    for cpc, nums in by_cpc.items():
        sampled.extend(random.sample(nums, min(per_group, len(nums))))

    # 부족하면 전체에서 무작위 보충
    all_nums = [n for n, _ in rows]
    sampled_set = set(sampled)
    remainder   = [n for n in all_nums if n not in sampled_set]
    random.shuffle(remainder)
    sampled += remainder[: max(0, total - len(sampled))]

    return sampled[:total]


def fetch_one(es, app_num):
    """출원번호로 ES v1 문서 1건 조회"""
    res = es.search(
        index=ES_INDEX,
        body={
            "query": {"term": {"ApplicationNumber": app_num}},
            "_source": FIELDS,
            "size": 1,
        },
    )
    hits = res["hits"]["hits"]
    if not hits:
        return None
    return hits[0]["_source"]


def main():
    parser = argparse.ArgumentParser(description="ES v1 명세서 수집기")
    parser.add_argument("--count",  type=int, default=30, help="수집 건수 (기본 30)")
    parser.add_argument("--seed",   type=int, default=42, help="랜덤 시드")
    parser.add_argument("--resume", action="store_true",   help="이미 수집된 파일 건너뜀")
    args = parser.parse_args()

    random.seed(args.seed)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    rows    = load_app_numbers()
    sampled = sample_by_cpc(rows, total=args.count)
    print(f"샘플 {len(sampled)}건 선택 완료")

    es = Elasticsearch(ES_URL, basic_auth=(ES_USERNAME, ES_PASSWORD), verify_certs=False)

    ok, skip, fail = 0, 0, 0
    for app_num in sampled:
        out_path = RAW_DIR / f"{app_num}.json"

        if args.resume and out_path.exists():
            skip += 1
            continue

        doc = fetch_one(es, app_num)
        if doc is None:
            print(f"  [MISS] {app_num}")
            fail += 1
            continue

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

        print(f"  [OK]   {app_num}  {doc.get('Title', '')[:40]}")
        ok += 1

    print(f"\n완료 — 성공: {ok}, 스킵: {skip}, 미조회: {fail}")
    print(f"저장 위치: {RAW_DIR}")


if __name__ == "__main__":
    main()

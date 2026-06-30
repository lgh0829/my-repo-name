"""
전체 수집 — list.csv 2,919건 전량 → data/raw_all/<출원번호>.json
--resume 플래그로 중단 후 재개 가능
"""

import csv
import json
import argparse
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

ES_URL      = "http://192.168.0.163:9204"
ES_USERNAME = "elastic"
ES_PASSWORD = "Rx6U8blh53KmWzs1Brnj"
ES_INDEX    = "kr_pub_patents"

FIELDS = [
    "ApplicationNumber", "Title", "MainCPC", "SubCPC",
    "ApplicationDate", "ApplicantName", "AgentNames",
    "Abstract", "Claims", "TechnicalField", "Background",
    "Problem", "SolutionProblem", "Effects",
    "BriefDescriptionOfDrawings", "Embodiment", "Summary",
]

LIST_CSV = Path("/Users/leegh/cc-workspace/es-search/output/list.csv")
RAW_ALL  = Path(__file__).parent.parent / "data-all" / "raw"


def load_app_numbers():
    with open(LIST_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return [row["출원번호"].strip() for row in reader if row.get("출원번호", "").strip()]


def fetch_one(es, app_num):
    res = es.search(
        index=ES_INDEX,
        body={
            "query": {"term": {"ApplicationNumber": app_num}},
            "_source": FIELDS,
            "size": 1,
        },
    )
    hits = res["hits"]["hits"]
    return hits[0]["_source"] if hits else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true", help="이미 수집된 파일 건너뜀")
    args = parser.parse_args()

    RAW_ALL.mkdir(parents=True, exist_ok=True)

    app_numbers = load_app_numbers()
    total = len(app_numbers)
    print(f"수집 대상: {total}건")

    es = Elasticsearch(ES_URL, basic_auth=(ES_USERNAME, ES_PASSWORD), verify_certs=False)

    ok = skip = fail = 0
    for i, app_num in enumerate(app_numbers, 1):
        out_path = RAW_ALL / f"{app_num}.json"

        if args.resume and out_path.exists():
            skip += 1
            continue

        doc = fetch_one(es, app_num)
        if doc is None:
            print(f"  [{i}/{total}] MISS  {app_num}")
            fail += 1
            continue

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

        if i % 100 == 0 or i == total:
            print(f"  [{i}/{total}] OK  {app_num}  {doc.get('Title','')[:30]}")
        ok += 1

    print(f"\n완료 — 성공: {ok}, 스킵: {skip}, 미조회: {fail}")
    print(f"저장 위치: {RAW_ALL}")


if __name__ == "__main__":
    main()

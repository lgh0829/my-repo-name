"""
cluster_labeler.py
3,390건 출원에 C0~C4 클러스터 라벨을 부여해 output/cluster_labeled.csv를 생성한다.
옵션 A: 본문 특성 측정 → K-means(k=5, seed=42)
"""
import os, re, sys, json, time
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

load_dotenv()

ES_URL  = os.getenv("ES_URL", "http://192.168.0.163:9204")
ES_USER = os.getenv("ES_USERNAME", "elastic")
ES_PASS = os.getenv("ES_PASSWORD", "")

def es_search(index: str, body: dict) -> dict:
    resp = requests.post(
        f"{ES_URL}/{index}/_search",
        json=body,
        auth=(ES_USER, ES_PASS),
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()

# ──────────────────────────────────────────────
# 1. 출원번호 목록 수집
# ──────────────────────────────────────────────
DATE_FROM = "20160101"  # 이 날짜 이후(포함) 출원만 수집

def _after_2016(date_str: str) -> bool:
    """YYYYMMDD 문자열이 DATE_FROM 이상인지 확인. 파싱 실패 시 포함(True)."""
    s = str(date_str).strip().replace("-", "").replace(".", "")[:8]
    if len(s) < 8 or not s.isdigit():
        return True
    return s >= DATE_FROM

def load_application_numbers():
    records = []

    # 김앤장 xlsx (비고 != '의심'인 행만, 2016년 이후)
    xl = pd.read_excel("ref/김앤장_한국기업_출원목록.xlsx", dtype=str)
    xl = xl[xl["비고"] != "의심"]
    before = len(xl)
    xl = xl[xl["출원일"].apply(_after_2016)]
    print(f"[load] 김앤장: {before}건 → {len(xl)}건 (2016년 이후 필터)")
    for _, row in xl.iterrows():
        app_no = str(row["출원번호"]).strip()
        agent  = str(row.get("검색된_김앤장_변리사", "")).strip()
        title  = str(row.get("발명의명칭", "")).strip()
        records.append({"출원번호": app_no, "사무소": "김앤장", "대리인": agent,
                        "MainCPC": "", "발명명칭": title, "출원일": str(row["출원일"]).strip()})

    # jang (2016년 이후)
    jang = pd.read_csv("output/jang_patents_1000.csv", dtype=str)
    before = len(jang)
    jang = jang[jang["출원일자"].apply(_after_2016)]
    print(f"[load] jang: {before}건 → {len(jang)}건 (2016년 이후 필터)")
    for _, row in jang.iterrows():
        app_no = str(row["출원번호"]).strip()
        cpc    = str(row.get("CPC", "")).strip()
        title  = str(row.get("발명의 명칭", "")).strip()
        records.append({"출원번호": app_no, "사무소": "jang", "대리인": "장수길",
                        "MainCPC": cpc, "발명명칭": title, "출원일": str(row["출원일자"]).strip()})

    # leeandmok (2016년 이후)
    lm = pd.read_csv("output/leeandmok_patents_1000.csv", dtype=str)
    before = len(lm)
    lm = lm[lm["출원일자"].apply(_after_2016)]
    print(f"[load] leeandmok: {before}건 → {len(lm)}건 (2016년 이후 필터)")
    for _, row in lm.iterrows():
        app_no = str(row["출원번호"]).strip()
        cpc    = str(row.get("CPC", "")).strip()
        title  = str(row.get("발명의 명칭", "")).strip()
        records.append({"출원번호": app_no, "사무소": "leeandmok", "대리인": "리앤목특허법인",
                        "MainCPC": cpc, "발명명칭": title, "출원일": str(row["출원일자"]).strip()})

    df = pd.DataFrame(records).drop_duplicates(subset=["출원번호"])
    print(f"[load] 총 {len(df)}건 (김앤장 {(df.사무소=='김앤장').sum()}, "
          f"jang {(df.사무소=='jang').sum()}, leeandmok {(df.사무소=='leeandmok').sum()})")
    return df

# ──────────────────────────────────────────────
# 2. ES 배치 조회
# ──────────────────────────────────────────────
BODY_FIELDS = ["Background", "Problem", "Effects", "Embodiment", "MainCPC",
               "AgentNames", "Title", "ApplicationNumber"]

def fetch_batch(app_numbers: list) -> dict:
    """출원번호 리스트 → {출원번호: doc} 딕셔너리 반환 (두 인덱스 동시 조회, pub 우선)"""
    result = {}
    for index in ["kr_pub_patents", "kr_opn_patents"]:
        try:
            resp = es_search(index, {
                "query": {"terms": {"ApplicationNumber": app_numbers}},
                "_source": BODY_FIELDS,
                "size": len(app_numbers)
            })
            for hit in resp["hits"]["hits"]:
                src = hit["_source"]
                app = src.get("ApplicationNumber", "")
                if app and app not in result:  # pub 먼저 조회하므로 pub 우선
                    result[app] = src
        except Exception as e:
            print(f"[warn] {index} 조회 오류: {e}", file=sys.stderr)
    return result

# ──────────────────────────────────────────────
# 3. 특성 측정 (계획서 정규식 그대로)
# ──────────────────────────────────────────────
def measure(bg: str, prob: str, eff: str, emb: str) -> dict:
    return {
        "cite_pat":   1 if re.search(r"특허문헌|선행기술문헌|공개특허|등록특허|특허\s*제?\s*\d|KR\s*\d{2}|특개|일본 특허|미국 특허", bg) else 0,
        "p_direct":   1 if re.search(r"문제(가|점이|점을|점도)\s*(있었|있다|발생|존재)", prob+" "+bg) else 0,
        "p_indirect": 1 if re.search(r"(요구|필요|요청)(되고|된다|되었|하고 있|성이)", prob+" "+bg) else 0,
        "multi_emb":  1 if len(re.findall(r"제\s*[1-9][0-9]?\s*(실시\s*예|실시\s*형태|구현\s*예|실시예|실시형태|구현예)", emb)) >= 2 else 0,
        "eff_filled": 1 if len(eff.strip()) > 10 else 0,
        "eff_qual":   1 if re.search(r"현저히|크게|효과적으로|용이하게|향상|개선|우수", eff) else 0,
        "sil_hyeong": 1 if re.search(r"실시\s*형태", emb) else 0,
        "sil_ye":     1 if re.search(r"실시\s*예", emb) else 0,
        "term_def":   1 if re.search(r"(본\s*명세서에서\s*사용되는\s*용어|용어의?\s*정의|본\s*발명에서\s*사용되는\s*용어)", emb[:1200]) else 0,
        "fig_list":   1 if re.search(r"도\s*\d+[은는이가]\s*.{2,20}(도|면|사시도|단면도|평면도|블록도)", emb[:800]) else 0,
        "bracket":    1 if re.search(r"\(\d+\)", emb) else 0,
        "inline":     1 if re.search(r"도\s*\d+[은는을를이가에서]", emb) else 0,
        "bg_len": len(bg), "emb_len": len(emb), "tf_len": 0,
    }

# ──────────────────────────────────────────────
# 4. 클러스터 번호 매핑 (K-means 라벨 → C0~C4)
#    클러스터 특성 평균 기반으로 논문 정의에 맞춰 매핑
# ──────────────────────────────────────────────
CLUSTER_NAMES = {
    "C0": "장문 간접형",
    "C1": "JP 번역체",
    "C2": "국내 표준",
    "C3": "JP 무효과형",
    "C4": "배경기술 중심",
}

def map_kmeans_to_clusters(df_feat: pd.DataFrame, km_labels: np.ndarray) -> np.ndarray:
    """
    K-means 라벨(0~4) → 계획서 정의 C0~C4 매핑.
    각 km 클러스터의 특성 평균으로 정의에 가장 가까운 C레이블을 찾는다.
    """
    feat_cols = [c for c in df_feat.columns if c != "app_no"]
    centers = {}
    for km_id in range(5):
        mask = km_labels == km_id
        centers[km_id] = df_feat[feat_cols][mask].mean()

    # 규칙 기반 매핑 (각 center의 특성 평균으로 판단)
    mapping = {}
    for km_id, c in centers.items():
        # C3: sil_hyeong 높고 eff_filled 낮음
        # C1: sil_hyeong 높고 cite_pat 높고 eff_filled 높음
        # C4: bg_len 최대, emb_len 최소
        # C0: p_indirect 높고 emb_len 최대
        # C2: sil_ye 높고 나머지
        pass

    # 단순히 최근접 매핑 대신, 우선순위 규칙으로 매핑
    center_df = pd.DataFrame(centers).T

    # C4: bg_len 최대인 클러스터
    c4_km = center_df["bg_len"].idxmax()
    # C3: sil_hyeong 높고 eff_filled 최소
    remaining = [i for i in range(5) if i != c4_km]
    c3_km = center_df.loc[remaining, "eff_filled"].idxmin()
    remaining = [i for i in remaining if i != c3_km]
    # C1: sil_hyeong 높고 cite_pat 높음 (C3 제외 후)
    c1_km = (center_df.loc[remaining, "sil_hyeong"] + center_df.loc[remaining, "cite_pat"]).idxmax()
    remaining = [i for i in remaining if i != c1_km]
    # C0: emb_len 최대
    c0_km = center_df.loc[remaining, "emb_len"].idxmax()
    remaining = [i for i in remaining if i != c0_km]
    # C2: 나머지
    c2_km = remaining[0]

    km_to_c = {c0_km: "C0", c1_km: "C1", c2_km: "C2", c3_km: "C3", c4_km: "C4"}
    print(f"[map] K-means → C 매핑: {km_to_c}")
    return np.array([km_to_c[l] for l in km_labels])

# ──────────────────────────────────────────────
# 5. 메인
# ──────────────────────────────────────────────
def main():
    df_meta = load_application_numbers()
    app_numbers = df_meta["출원번호"].tolist()

    # ES 배치 조회 (100건씩)
    print("[fetch] ES 조회 시작...")
    docs = {}
    batch_size = 100
    total = len(app_numbers)
    for i in range(0, total, batch_size):
        batch = app_numbers[i:i+batch_size]
        fetched = fetch_batch(batch)
        docs.update(fetched)
        if (i // batch_size) % 10 == 0:
            print(f"  {i+len(batch)}/{total} 조회됨 ({len(docs)} 매칭)", end="\r")
    print(f"\n[fetch] ES에서 {len(docs)}/{total}건 조회 성공")

    # 특성 측정
    print("[measure] 특성 측정 중...")
    feat_rows = []
    no_doc = []
    for app_no in app_numbers:
        doc = docs.get(app_no, {})
        if not doc:
            no_doc.append(app_no)
            # 빈 특성으로 대체
            feat = measure("", "", "", "")
        else:
            bg  = doc.get("Background", "") or ""
            prob= doc.get("Problem", "") or ""
            eff = doc.get("Effects", "") or ""
            emb = doc.get("Embodiment", "") or ""
            feat = measure(bg, prob, eff, emb)
        feat["app_no"] = app_no
        feat_rows.append(feat)
    print(f"[measure] 완료. ES 미매칭: {len(no_doc)}건")

    df_feat = pd.DataFrame(feat_rows)
    feat_cols = [c for c in df_feat.columns if c != "app_no"]

    # K-means 클러스터링
    print("[kmeans] K-means(k=5, seed=42) 실행...")
    X = df_feat[feat_cols].values.astype(float)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    km = KMeans(n_clusters=5, random_state=42, n_init=10)
    km_labels = km.fit_predict(X_scaled)

    # 클러스터 매핑
    c_labels = map_kmeans_to_clusters(df_feat, km_labels)

    # MainCPC: ES에서 가져오기 (xlsx/csv에 없는 경우 보완)
    def get_cpc(app_no, meta_cpc):
        if meta_cpc and meta_cpc != "nan":
            return meta_cpc
        doc = docs.get(app_no, {})
        return doc.get("MainCPC", "") or ""

    # 결과 DataFrame 구성
    df_result = df_meta.copy()
    df_result["클러스터"] = c_labels
    df_result["MainCPC"] = [
        get_cpc(row["출원번호"], row["MainCPC"])
        for _, row in df_result.iterrows()
    ]

    # 발명명칭 보완 (ES Title)
    def get_title(row):
        if row["발명명칭"] and row["발명명칭"] != "nan":
            return row["발명명칭"]
        doc = docs.get(row["출원번호"], {})
        return doc.get("Title", "") or ""
    df_result["발명명칭"] = df_result.apply(get_title, axis=1)

    # 저장
    out_cols = ["출원번호", "출원일", "사무소", "대리인", "MainCPC", "클러스터", "발명명칭"]
    df_result[out_cols].to_csv("output/cluster_labeled.csv", index=False, encoding="utf-8-sig")
    print(f"[save] output/cluster_labeled.csv 저장 완료 ({len(df_result)}건)")

    # 검증 출력
    print("\n[검증] 클러스터 × 사무소 분포:")
    pivot = pd.crosstab(df_result["클러스터"], df_result["사무소"])
    print(pivot)
    print("\n[검증] 클러스터별 건수:")
    print(df_result["클러스터"].value_counts().sort_index())

    # 특성 평균 검증
    print("\n[검증] 클러스터별 주요 특성 평균 (상위 5개):")
    df_feat["클러스터"] = c_labels
    check_cols = ["cite_pat", "sil_hyeong", "sil_ye", "eff_filled", "bg_len", "emb_len"]
    print(df_feat.groupby("클러스터")[check_cols].mean().round(3))

if __name__ == "__main__":
    main()

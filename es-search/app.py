"""
명세서 본문 클러스터 뷰어
streamlit run app.py
"""
import os
import re
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from typing import Optional
from pathlib import Path

# 스크립트 위치 기준으로 절대 경로 설정 (CWD에 무관하게 동작)
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

ES_URL  = os.getenv("ES_URL", "http://192.168.0.163:9204")
ES_USER = os.getenv("ES_USERNAME", "elastic")
ES_PASS = os.getenv("ES_PASSWORD", "")

CLUSTER_INFO = {
    "A 선행인용형":      {"name": "선행인용형",    "desc": "배경기술에 선행 특허문헌 명시 인용", "color": "#0d6efd"},
    "B 직접과제형":      {"name": "직접과제형",    "desc": "과제를 직접적으로 서술 (문제가 있었다)", "color": "#dc3545"},
    "C 간접·표준형":     {"name": "간접·표준형",   "desc": "간접 과제 + 표준 실시예 구성", "color": "#198754"},
    "JP 번역체(v2제외)": {"name": "JP 번역체",     "desc": "실시형태 + 일본 번역 패턴 (v2 분석 제외)", "color": "#6c757d"},
}
CLUSTER_COL = "클러스터_v2"  # v2 CSV 컬럼명

FIELD_LABELS = [
    ("Background",      "배경기술"),
    ("Problem",         "해결하려는 과제"),
    ("SolutionProblem", "과제의 해결 수단"),
    ("Effects",         "발명의 효과"),
    ("Embodiment",      "실시예"),
]

# ──────────────────────────────────────────────
# ES 연결 상태 확인 (앱 시작 시 1회)
# ──────────────────────────────────────────────
@st.cache_data(ttl=60)
def check_es_connection() -> bool:
    try:
        r = requests.get(ES_URL, auth=(ES_USER, ES_PASS), timeout=5)
        return r.status_code == 200
    except Exception:
        return False

# ──────────────────────────────────────────────
# ES 조회
# ──────────────────────────────────────────────
def es_get(app_no: str) -> Optional[dict]:
    """단건 출원 조회 (pub 우선). ES 불가 시 None 반환."""
    body = {
        "query": {"term": {"ApplicationNumber": app_no}},
        "_source": ["Background", "Problem", "SolutionProblem", "Effects",
                    "Embodiment", "Title", "ApplicantName", "AgentNames",
                    "MainCPC", "ApplicationNumber", "ApplicationDate"],
        "size": 1,
    }
    for index in ["kr_pub_patents", "kr_opn_patents"]:
        try:
            r = requests.post(
                f"{ES_URL}/{index}/_search",
                json=body,
                auth=(ES_USER, ES_PASS),
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
            r.raise_for_status()
            hits = r.json()["hits"]["hits"]
            if hits:
                return hits[0]["_source"]
        except Exception:
            pass
    return None

# ──────────────────────────────────────────────
# 데이터 로드
# ──────────────────────────────────────────────
@st.cache_data
def load_labeled() -> pd.DataFrame:
    df = pd.read_csv(BASE_DIR / "output" / "cluster_labeled_v2.csv", dtype=str)
    df = df.fillna("")
    return df

# ──────────────────────────────────────────────
# 화면 공통
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="명세서 클러스터 뷰어",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.cluster-card {
    border-left: 6px solid;
    padding: 10px 16px;
    margin-bottom: 10px;
    border-radius: 4px;
    background: #f8f9fa;
}
.body-section h4 { margin-top: 0; }
.empty-text { color: #888; font-style: italic; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 사이드바 — 필터
# ──────────────────────────────────────────────
with st.sidebar:
    st.title("필터")
    df_all = load_labeled()

    office_opts = ["전체"] + sorted(df_all["사무소"].unique().tolist())
    sel_office = st.selectbox("사무소", office_opts)

    cpc_input = st.text_input("CPC 접두어 (예: H01L)", "")
    search_kw = st.text_input("발명명칭 검색", "")

# ──────────────────────────────────────────────
# 화면 1 — 클러스터 선택
# ──────────────────────────────────────────────
if "selected_cluster" not in st.session_state:
    st.session_state.selected_cluster = None
if "selected_app" not in st.session_state:
    st.session_state.selected_app = None

# 필터 적용
df_filtered = df_all.copy()
if sel_office != "전체":
    df_filtered = df_filtered[df_filtered["사무소"] == sel_office]
if cpc_input.strip():
    df_filtered = df_filtered[df_filtered["MainCPC"].str.startswith(cpc_input.strip(), na=False)]
if search_kw.strip():
    df_filtered = df_filtered[df_filtered["발명명칭"].str.contains(search_kw.strip(), na=False)]

es_available = check_es_connection()

st.title("📄 명세서 본문 클러스터 뷰어")
if not es_available:
    st.warning("⚠️ Elasticsearch에 연결할 수 없습니다. 클러스터 목록·출원 목록은 로컬 CSV로 정상 표시되며, 출원 상세(본문 5항목)는 이용할 수 없습니다.")

# 클러스터 카드
st.subheader("클러스터 선택")
cluster_keys = list(CLUSTER_INFO.keys())
cols = st.columns(len(cluster_keys))
for i, ck in enumerate(cluster_keys):
    info = CLUSTER_INFO[ck]
    cnt  = len(df_filtered[df_filtered[CLUSTER_COL] == ck])
    with cols[i]:
        is_sel = st.session_state.selected_cluster == ck
        btn_label = f"{'✅ ' if is_sel else ''}{ck} {info['name']}\n\n{cnt}건"
        if st.button(btn_label, key=f"btn_{ck}", use_container_width=True):
            if st.session_state.selected_cluster == ck:
                st.session_state.selected_cluster = None
                st.session_state.selected_app = None
            else:
                st.session_state.selected_cluster = ck
                st.session_state.selected_app = None
        st.caption(info["desc"])

st.divider()

# ──────────────────────────────────────────────
# 화면 2 — 출원 목록
# ──────────────────────────────────────────────
sel_cluster = st.session_state.selected_cluster
if sel_cluster:
    info = CLUSTER_INFO[sel_cluster]
    st.subheader(f"{sel_cluster} — {info['name']}")
    st.caption(info["desc"])

    df_cluster = df_filtered[df_filtered[CLUSTER_COL] == sel_cluster].copy()
    st.write(f"**{len(df_cluster)}건** (필터 적용 후)")

    # 정렬
    sort_col = st.selectbox("정렬 기준", ["출원번호", "출원일", "발명명칭", "사무소", "대리인", "MainCPC"],
                            key="sort_col")
    df_cluster = df_cluster.sort_values(sort_col)

    # 테이블 표시
    display_cols = ["출원번호", "출원일", "발명명칭", "사무소", "대리인", "MainCPC"]
    df_show = df_cluster[display_cols].reset_index(drop=True)

    # 클릭 선택
    sel_idx = st.selectbox(
        "출원번호 클릭 (상세 보기)",
        options=df_show["출원번호"].tolist(),
        index=None,
        placeholder="출원번호를 선택하세요…",
        key="app_select",
    )
    if sel_idx:
        st.session_state.selected_app = sel_idx

    st.dataframe(df_show, use_container_width=True, height=300)

    st.divider()

# ──────────────────────────────────────────────
# 화면 3 — 출원 상세
# ──────────────────────────────────────────────
sel_app = st.session_state.selected_app
if sel_app:
    st.subheader(f"출원 상세 — {sel_app}")

    meta_row = df_all[df_all["출원번호"] == sel_app]
    cluster_label = meta_row[CLUSTER_COL].values[0] if len(meta_row) else "?"
    cluster_name  = CLUSTER_INFO.get(cluster_label, {}).get("name", "")

    if not es_available:
        # ── 오프라인 폴백: CSV 메타만 표시 ──────────────
        csv_title  = meta_row["발명명칭"].values[0] if len(meta_row) else "—"
        csv_agent  = meta_row["대리인"].values[0]   if len(meta_row) else "—"
        csv_office = meta_row["사무소"].values[0]   if len(meta_row) else "—"
        csv_cpc    = meta_row["MainCPC"].values[0]  if len(meta_row) else "—"
        csv_date   = meta_row["출원일"].values[0]   if len(meta_row) else "—"

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("발명명칭", csv_title[:40] + ("…" if len(csv_title) > 40 else ""))
        m2.metric("클러스터", f"{cluster_label} {cluster_name}")
        m3.metric("CPC", csv_cpc or "—")
        m4.metric("출원일", csv_date or "—")
        st.caption(f"사무소: {csv_office}　대리인: {csv_agent}")
        st.info("ES에 연결할 수 없어 본문(배경기술·과제·효과·실시예)을 불러올 수 없습니다.")
    else:
        # ── 온라인: ES에서 본문 조회 ──────────────────
        with st.spinner("ES에서 본문 조회 중..."):
            doc = es_get(sel_app)

        if doc is None:
            # 연결은 됐지만 해당 출원이 인덱스에 없는 경우
            csv_title  = meta_row["발명명칭"].values[0] if len(meta_row) else "—"
            csv_cpc    = meta_row["MainCPC"].values[0]  if len(meta_row) else "—"
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("발명명칭", csv_title[:40] + ("…" if len(csv_title) > 40 else ""))
            m2.metric("클러스터", f"{cluster_label} {cluster_name}")
            m3.metric("CPC", csv_cpc or "—")
            m4.metric("출원일", meta_row["출원일"].values[0] if len(meta_row) else "—")
            st.warning("ES 인덱스에서 해당 출원을 찾을 수 없습니다.")
        else:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("발명명칭", doc.get("Title", "") or "—")
            m2.metric("출원인", doc.get("ApplicantName", "") or "—")
            m3.metric("클러스터", f"{cluster_label} {cluster_name}")
            m4.metric("CPC", doc.get("MainCPC", "") or "—")

            agents_raw = doc.get("AgentNames", "") or ""
            agents = [a.strip() for a in agents_raw.split("¶") if a.strip()]
            st.caption(f"대리인: {', '.join(agents) if agents else '—'}")

            st.divider()

            # 본문 5항목 탭
            tab_labels = [label for _, label in FIELD_LABELS]
            tabs = st.tabs(tab_labels)
            for tab, (field, label) in zip(tabs, FIELD_LABELS):
                with tab:
                    text = doc.get(field, "") or ""
                    if not text.strip():
                        st.markdown('<p class="empty-text">(미기재)</p>', unsafe_allow_html=True)
                    else:
                        if field == "Embodiment":
                            st.text_area(
                                label=f"{label} ({len(text):,}자)",
                                value=text,
                                height=500,
                                key=f"ta_{field}_{sel_app}",
                            )
                        else:
                            st.text_area(
                                label=f"{label} ({len(text):,}자)",
                                value=text,
                                height=250,
                                key=f"ta_{field}_{sel_app}",
                            )

# ──────────────────────────────────────────────
# 클러스터 미선택 안내
# ──────────────────────────────────────────────
if not sel_cluster:
    st.info("위 카드에서 클러스터를 선택하면 출원 목록이 표시됩니다.")
    st.markdown("""
| 클러스터 | 핵심 특성 |
|---|---|
| **A 선행인용형** | 배경기술에 선행 특허문헌 명시 인용 |
| **B 직접과제형** | 과제를 직접적으로 서술 (문제가 있었다) |
| **C 간접·표준형** | 간접 과제 + 표준 실시예 구성 |
| **JP 번역체(v2제외)** | 실시형태 + 일본 번역 패턴 (v2 분석 제외) |
""")

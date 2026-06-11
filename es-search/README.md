# 명세서 본문 클러스터 뷰어

특허 명세서를 본문 작성 스타일 클러스터별로 분리하고, 출원별 본문 5개 항목을 열람하는 도구.

## 실행

```bash
cd es-search
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속.

## 클러스터 정의 (C0~C4)

| 클러스터 | 이름 | 핵심 특성 | 주 사무소 |
|---|---|---|---|
| C1 | JP 번역체 | 실시형태 + 선행기술 특허문헌 인용 + 간접 과제 | jang 93% |
| C3 | JP 무효과형 | 실시형태 + 효과 섹션 없음 | jang 79% |
| C2 | 국내 표준 | 실시예 + 효과 기재 + 실시형태 미사용 | leeandmok·김앤장 공유 |
| C4 | 배경기술 중심 | 배경기술 최장 + 실시예 최단 + 직접 과제 | 김앤장 83% |
| C0 | 장문 간접형 | 간접 과제 + 긴 실시예 | 3사 혼재(경계군) |

## 클러스터 라벨 재생성

```bash
python3 cluster_labeler.py
```

- 옵션 A (K-means): 12개 이진 특성 + 3개 분량 특성 측정 → z-score 표준화 → K-means(k=5, seed=42)
- 결과 저장: `output/cluster_labeled.csv`

## 분석 대상

- 총 3,390건: 김앤장 1,390건 / jang 1,000건 / leeandmok 1,000건
- 인덱스: `kr_pub_patents` (pub 우선), `kr_opn_patents`

## 본문 5개 항목

| 화면 표시명 | ES 필드 |
|---|---|
| 배경기술 | `Background` |
| 해결하려는 과제 | `Problem` |
| 과제의 해결 수단 | `SolutionProblem` |
| 발명의 효과 | `Effects` |
| 실시예 | `Embodiment` |

`SolutionProblem`은 jang·leeandmok에서 거의 0% 채움 — 비면 "(미기재)" 표시.

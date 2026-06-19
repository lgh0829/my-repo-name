# App Building Harness

특허 명세서 스타일 분석 결과를 간단한 UI로 보여줄 때 사용한다.

## 기본 앱 흐름

```text
클러스터 선택 → 출원 목록 → 출원 상세
```

출원 상세는 본문 5개 항목을 분리 표시한다.

| 화면 표시명 | 필드 |
|---|---|
| 배경기술 | `Background` / v2 `background_art.text` |
| 해결하려는 과제 | `Problem` / v2 `technicalproblem.text` |
| 과제의 해결 수단 | `SolutionProblem` / v2 `technicalsolution.text` |
| 발명의 효과 | `Effects` / v2 `advantageouseffects.text` |
| 실시예 | `Embodiment` / v2 `embodimentdescription.text` |

## 구현 권장

- Streamlit 우선.
- 클러스터 라벨은 미리 계산해 `output/cluster_labeled.csv`로 저장한다.
- 본문 전문은 CSV에 넣지 말고 출원번호로 ES 또는 로컬 DB에서 조회한다.
- Embodiment는 길기 때문에 스크롤 영역이나 지연 로딩을 사용한다.
- `SolutionProblem`은 비어 있어도 정상이다. 화면에는 `(미기재)`로 표시한다.

## 주의

- 발명자명은 표시하지 않는다.
- ES에는 조회만 수행한다.
- v2를 쓰면 `scripts/db/build_local_db_v2.py` 또는 `data/local/`의 로컬 DB를 우선 사용한다.

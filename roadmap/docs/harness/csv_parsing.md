# Jira CSV 파싱 규칙

Jira export(`Jira_2026-QN.csv`)는 까다롭다. 아래를 지킨다.

---

## 파싱 주의

- **중복 헤더**: 스프린트·레이블·댓글·로그 작업 등이 다중 컬럼으로 반복된다. `csv.DictReader`는 같은 이름 컬럼을 덮어쓰므로, `csv.reader`로 헤더 인덱스를 직접 수집해 같은 이름 컬럼은 "첫 비어있지 않은 값"(단일값) 또는 "전체 수집"(레이블·스프린트)으로 처리한다.
- **셀 내 줄바꿈**: 설명 필드에 줄바꿈이 많다. 파일 줄 수 ≠ 이슈 수. 행수는 `csv` 파서가 센 레코드 수 기준.
- **날짜 포맷**: `DD/M월/YY h:mm 오전|오후` (한국어). 한글 월(`1월`~`12월`) 매핑 필요. 오전/오후는 cycle time(일 단위) 계산엔 무시 가능.

---

## 핵심 컬럼

`이슈 키` / `요약` / `상태` / `상태 범주` / `담당자` / `우선 순위` / `사용자정의 필드 (Story point estimate)` / `스프린트`(다중) / `Parent summary`(Epic) / `만듦` / `해결됨` / `레이블`(다중).

> `사용자정의 필드 (로드맵)`·`사용자정의 필드 (목표)`는 비어 있는 경우가 많다 — OKR 매핑은 PO가 의미 기반으로 수행한다(`okr_mapping.md`).

---

## 상태 체계 → 집계 규칙

| 상태 | 집계 |
|---|---|
| `완료`, `DEV 배포완료` | 완료 |
| `QA`, `진행 중` | 진행 |
| `해야 할 일` | 미착수 |
| `드롭` | 중단 (별도 집계 — 사유 점검 대상) |

`상태 범주`(완료/진행 중/해야 할 일)는 보조 검증용. 세부 판단은 `상태`로 한다.

---

## SP(Story point) 주의

입력률이 낮다(과거 분기 45% 수준). 합계·번다운은 **보조 지표로만** 쓰고, 완료 건수를 1차 지표로 삼는다. 입력률 자체를 데이터 위생 회고 항목으로 보고한다.

## 참고 스니펫

```python
import csv
with open(path, encoding='utf-8') as f:
    rows = list(csv.reader(f))
hdr, data = rows[0], rows[1:]
def col(name): return [i for i,h in enumerate(hdr) if h==name]
def fv(row,name):              # 첫 비어있지 않은 값
    for i in col(name):
        if i < len(row) and row[i].strip(): return row[i].strip()
    return ''
def allv(row,name):            # 다중 컬럼 전체 수집 (레이블·스프린트)
    return [row[i].strip() for i in col(name) if i<len(row) and row[i].strip()]
```

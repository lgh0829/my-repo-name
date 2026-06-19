# ES v1 Schema Harness (`kr_pub_patents`, `kr_opn_patents`)

구형 ES(v1)는 평탄 필드 구조다. 기존 리포트 재현, 과거 산출물 검증, v1 직접 조회가 필요할 때만 사용한다.

## 접속 정보

```env
ES_URL=http://192.168.0.163:9204
ES_USERNAME=elastic
ES_PASSWORD=Rx6U8blh53KmWzs1Brnj
ES_INDEX=kr_pub_patents
```

## 사용 가능한 인덱스

| 인덱스 | 용도 |
|---|---|
| `kr_pub_patents` | 공개특허. 스타일 분석 기본 대상 |
| `kr_opn_patents` | 공개공보. 김앤장 등 횡단 분석 보완 |

## 주요 필드

| 용도 | v1 필드 |
|---|---|
| 출원번호 | `ApplicationNumber` |
| 공개번호 | `OpenNumber` |
| 등록번호 | `RegisterNumber` |
| 출원일 | `ApplicationDate` |
| 공개일 | `OpenDate` |
| 등록일 | `RegisterDate` |
| 발명의 명칭 | `Title` |
| 출원인 | `ApplicantName` |
| 대리인 | `AgentNames` (`¶` 구분) |
| 담당 변리사 | `AttorneyName` |
| 발명자 | `InventorName` — 리포트 표시 금지 |
| CPC | `MainCPC`, `SubCPC` |
| 청구항 | `Claims` (`¶`로 청구항 구분) |
| 기술분야 | `TechnicalField` |
| 배경기술 | `Background` |
| 발명의 내용 | `Disclosure` |
| 해결하려는 과제 | `Problem` |
| 과제 해결 수단 | `SolutionProblem` |
| 발명의 효과 | `Effects` |
| 도면 설명 | `BriefDescriptionOfDrawings` |
| 실시예 | `Embodiment` |
| 요약 | `Summary` |

## 금지 필드

매핑에 보이더라도 분석 필터에 쓰지 않는다. 실제 데이터가 비어 있거나 기존 분석에서 오류를 만들었다.

```text
IPC_MAIN  -> MainCPC로 대체
IPC_SUB   -> SubCPC로 대체
CPC_MAIN  -> MainCPC로 대체
CPC_SUB   -> SubCPC로 대체
```

## AgentNames 쿼리

법인명 전체는 `match_phrase`를 쓴다.

```json
{ "match_phrase": { "AgentNames": "리앤목특허법인" } }
```

개인 변리사명은 `match`를 쓸 수 있다.

```json
{ "match": { "AgentNames": "장수길" } }
```

## 조회 예시

```json
GET /kr_pub_patents/_search
{
  "query": {
    "bool": {
      "must": [
        { "match_phrase": { "AgentNames": "리앤목특허법인" } },
        { "match_phrase_prefix": { "MainCPC": "H01L" } }
      ]
    }
  },
  "_source": ["ApplicationNumber", "Title", "Claims", "Embodiment", "MainCPC"],
  "size": 30
}
```


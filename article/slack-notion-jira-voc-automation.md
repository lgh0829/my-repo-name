---
aliases: Slack VOC 자동화 — Notion 기록 및 Jira 티켓 생성
작성일: 2026-03-06
수정일: 2026-03-07
상태: 검토
유형: 실무노하우
태그: n8n, slack, notion, jira, automation, voc
발행일:
---

# 코드 한 줄 없이 만드는 VOC 자동화 — Slack → Notion → Jira

## 핵심 메시지

> Slack 폼으로 VOC를 수집하면 Notion에 자동 기록되고, 버그·긴급 건은 Jira 티켓까지 자동 생성되는 자동화를 n8n으로 구축한 실전 기록.

## 독자와 상황

- **대상 독자:** 반복 업무를 자동화하고 싶은 기획자, 운영 담당자
- **독자가 겪는 문제:** VOC가 Slack으로 들어오는데 Notion에 옮기고 Jira 티켓을 따로 만드는 게 매번 번거롭다

---

## 왜 만들었나

팀에서 고객 문의(VOC)를 Slack으로 받고 있었다. 문제는 그 다음이었다. 누군가는 내용을 복사해서 Notion DB에 붙여넣고, 버그나 긴급 건이면 Jira 티켓까지 별도로 만들어야 했다. 하루에 몇 건 되지 않아도 이 반복 작업이 쌓이면 꽤 피로하다.

그래서 자동화를 구축했다. 목표는 단순했다.

1. Slack 폼으로 VOC 수집
2. 수집된 내용을 Notion DB에 자동 기록
3. 유형이 버그이고 긴급도가 높음이면 Jira 티켓 자동 생성

---

## 전체 흐름

```
사용자가 /voc 입력
    ↓
Slack Modal 팝업 (고객명 / 문의유형 / 긴급도 / 문의내용)
    ↓
n8n이 데이터 수신
    ↓
Gemini API로 제목 자동 생성 (40자 이내 요약)
    ↓
Notion DB에 기록
    ↓
버그 + 높음이면 → Jira 티켓 생성
    ↓
접수 완료 메시지를 해당 채널에 전송
```

{{ 전체 흐름 다이어그램 또는 n8n 워크플로우 B 전체 화면 캡처. 노드들이 연결된 전체 구조가 한눈에 보이는 화면 }}

사용하는 도구는 아래와 같다.

| 도구 | 역할 |
|---|---|
| Slack App | 폼 입력 UI (슬래시 커맨드 + Modal) |
| n8n (self-hosted) | 자동화 워크플로우 엔진 |
| Gemini API | 문의 내용 자동 요약 |
| Notion API | VOC DB 기록 |
| Jira Cloud API | 버그 티켓 자동 생성 |

---

## 삽질 포인트 1 — Workflow Builder 폼은 유료 플랜만 웹훅 지원

처음엔 Slack의 Workflow Builder로 폼을 만들었다. 필드도 만들었고, 보기도 좋았다. 문제는 폼 제출 결과를 외부로 보내는 "웹훅 전송" 스텝이 **유료 플랜에서만** 가능하다는 것이었다.

{{ Slack Workflow Builder에서 '단계 추가' 클릭 시 웹훅 전송 옵션이 없는 화면 캡처 }}

무료 플랜이라면 Workflow Builder 폼은 n8n과 연결할 수 없다. 그래서 방향을 바꿨다.

**해결책: Slack App을 직접 만들고, 슬래시 커맨드 + Modal 방식으로 전환**

사용자 경험은 동일하다. `/voc`를 입력하면 팝업 폼이 열리고, 필드를 채운 뒤 제출하면 된다. 대신 폼이 Workflow Builder가 아닌 Slack의 Block Kit Modal로 구현된다.

{{ Slack에서 /voc 입력 후 Modal이 열린 화면 캡처. 고객명/문의유형/긴급도/문의내용 필드가 보이는 완성된 폼 }}

---

## Slack App 설정

### 앱 생성

`api.slack.com/apps`에서 앱을 만든다. From scratch 선택 후 이름과 워크스페이스를 지정하면 된다.

{{ api.slack.com/apps 앱 생성 화면 — From scratch 선택 단계 캡처 }}

### 필요한 설정 세 가지

**① Slash Command**
- Command: `/voc`
- Request URL: n8n의 `voc-trigger` Webhook URL

{{ Slash Commands 설정 화면 캡처 — Command, Request URL 입력된 상태 }}

**② Interactivity**
- ON으로 활성화
- Request URL: n8n의 `voc-submit` Webhook URL

{{ Interactivity & Shortcuts 설정 화면 캡처 — 토글 ON 및 Request URL 입력된 상태 }}

**③ Bot Token Scopes**
- `commands`: 슬래시 커맨드 사용
- `chat:write`: 채널에 메시지 전송
- `users:read`: 제출자 실명 조회

{{ OAuth & Permissions 화면에서 Bot Token Scopes에 세 가지 권한이 추가된 상태 캡처 }}

앱을 워크스페이스에 설치하면 Bot User OAuth Token이 발급된다. 이 토큰이 모든 Slack API 호출에 쓰인다.

---

## n8n 워크플로우 설계

워크플로우는 두 개로 나뉜다.

### 워크플로우 A — 모달 열기 (voc-trigger)

```
Webhook (voc-trigger)
    ↓
Respond to Webhook (즉시 빈 응답)
    ↓
HTTP Request (Slack views.open API 호출)
```

{{ n8n 워크플로우 A 전체 화면 캡처. 세 개 노드가 연결된 구조 }}

`/voc` 명령이 들어오면 Slack이 이 웹훅으로 POST를 보낸다. n8n은 즉시 빈 응답(`{}`)을 반환하고, 동시에 Slack `views.open` API를 호출해 모달을 띄운다.

### 워크플로우 B — 데이터 처리 (voc-submit)

```
Webhook (voc-submit)
    ↓
Respond to Webhook (즉시 {"response_action": "clear"})
    ↓
Code 노드 (payload 파싱)
    ↓
HTTP Request (Slack users.info — 실명 조회)
    ↓
HTTP Request (Gemini API — 제목 요약)
    ↓
Notion 노드 (DB 기록)
    ↓
IF 노드 (버그 + 높음 조건)
    ↓ True
Jira 노드 (티켓 생성)
    ↓
HTTP Request (chat.postMessage — 완료 알림)
```

{{ n8n 워크플로우 B 전체 화면 캡처. 모든 노드가 연결된 구조 }}

---

## 삽질 포인트 2 — trigger_id는 3초 안에 써야 한다

모달을 열 때 Slack이 보내는 `trigger_id`는 **발급 후 3초 안에** `views.open` API에 전달해야 유효하다. 3초가 지나면 `invalid_trigger_id` 에러가 발생한다.

n8n의 Test URL로 테스트할 때 이 문제가 자주 발생한다. "Listen for test event" 버튼을 누른 후 Slack에서 `/voc`를 입력하고, n8n으로 돌아와 다음 노드를 실행하는 사이에 3초가 지나버리기 때문이다.

{{ n8n 실행 로그에서 invalid_trigger_id 에러가 발생한 화면 캡처 }}

**해결책: Production URL로 전환 + 워크플로우 Activate**

Production URL을 쓰면 n8n이 즉시 자동 처리하므로 3초 안에 처리가 완료된다. Slack App의 Slash Command URL도 Test URL에서 Production URL로 교체해야 한다.

- Test URL: `https://n8n.도메인/webhook-test/voc-trigger`
- Production URL: `https://n8n.도메인/webhook/voc-trigger`

{{ n8n 워크플로우 우측 상단 Activate 토글이 ON 상태인 화면 캡처 }}

---

## 삽질 포인트 3 — n8n JSON body 안의 표현식 문법

n8n에서 HTTP Request 노드의 JSON body 안에 동적 값을 넣을 때 문법이 헷갈린다.

**UI 입력 필드**에서는 `=` 를 붙여 expression 모드로 전환한다.
```
={{ $json.body.trigger_id }}
```

그런데 **JSON body 안 문자열**에 그대로 쓰면 `=` 기호가 값에 포함되어 버린다.
```json
"trigger_id": "={{ $json.body.trigger_id }}"  // ❌ =10641... 로 전송됨
"trigger_id": "{{$json.body.trigger_id}}"     // ✅ 올바른 방법
```

{{ n8n HTTP Request 노드 JSON body 입력창 하단 미리보기에서 trigger_id 값 앞에 = 기호가 붙어있는 화면 캡처 }}

JSON body 안에서는 `=` 없이 `{{ }}` 만 사용한다.

---

## 삽질 포인트 4 — 모달 제출 후 "연결 문제" 알림

Slack은 모달 제출 후 **3초 안에** 응답을 받아야 한다. 응답이 없으면 "연결하는데 문제가 발생했습니다" 알림이 뜨고 폼이 닫히지 않는다.

{{ Slack 모달에서 "연결하는데 문제가 발생했습니다. 다시 시도하시겠습니까?" 알림이 표시된 화면 캡처 }}

워크플로우 B는 Gemini, Notion, Jira 순서로 API를 호출하므로 3초를 넘기기 쉽다.

**해결책: Respond to Webhook 노드를 Webhook 바로 다음에 배치**

`{"response_action": "clear"}` 를 즉시 반환하면 Slack이 모달을 닫는다. 나머지 처리는 백그라운드에서 계속 진행된다.

{{ n8n에서 Respond to Webhook 노드 설정 화면 캡처 — Response Body에 {"response_action": "clear"} 입력된 상태 }}

단, 이를 위해 Webhook 노드의 **Response Mode**를 `Using Respond to Webhook Node`로 변경해야 한다.

{{ Webhook 노드 Settings 탭에서 Response Mode가 "Using Respond to Webhook Node"로 설정된 화면 캡처 }}

---

## Gemini로 제목 자동 생성

Notion DB의 제목을 사람이 직접 쓰지 않아도 된다. 문의 내용을 Gemini에 넘기면 40자 이내로 요약한 제목을 만들어준다.

```
[버그][높음] 청구항 발명 유형별 자동 구분 기능 요청
```

{{ Notion DB에 VOC가 기록된 화면 캡처. Gemini가 생성한 제목이 포함된 실제 행 }}

n8n에서 Gemini API를 호출할 때 JSON body 안에 동적 값을 넣으려면 Code 노드에서 미리 객체를 만들어 넘기는 방식이 안정적이다. 문의 내용에 따옴표나 줄바꿈이 포함되면 직접 JSON 문자열에 넣을 때 파싱 오류가 발생하기 때문이다.

---

## 채널 ID를 모달에 담아 전달하기

완료 메시지를 `/voc`를 실행한 채널에 보내려면 채널 ID가 필요하다. 그런데 채널 ID는 슬래시 커맨드 payload(워크플로우 A)에만 있고, 모달 제출 payload(워크플로우 B)에는 없다.

**해결책: `private_metadata`에 채널 ID를 담아 모달에 심기**

views.open 호출 시 모달 view 객체에 `private_metadata` 필드를 추가한다.

```json
"view": {
  "type": "modal",
  "private_metadata": "{{$json.body.channel_id}}",
  ...
}
```

모달이 제출되면 `payload.view.private_metadata`에서 채널 ID를 꺼낼 수 있다. 이 값을 Code 노드에서 추출해 두면 `chat.postMessage` 호출 시 활용할 수 있다.

---

## 완성된 결과

`/voc`를 입력하면 팝업 폼이 열린다. 고객명, 문의 유형, 긴급도, 문의 내용을 입력하고 제출하면:

- Notion DB에 자동 기록된다. 제목은 Gemini가 요약해서 달아준다.
- 버그이고 긴급도가 높으면 Jira에 `[fix]` 타입의 Bug 티켓이 생성된다.
- 접수한 채널에 완료 메시지와 Jira 티켓 링크가 전송된다.

{{ Slack 채널에 완료 메시지와 Jira 티켓 링크가 전송된 화면 캡처 }}

{{ Jira에 자동 생성된 Bug 티켓 화면 캡처 — Summary, Priority, Description이 채워진 상태 }}

사람이 할 일은 폼 작성뿐이다.

---

## 목차

1. 왜 만들었나
2. 전체 흐름
3. 삽질 포인트 1 — Workflow Builder 폼의 한계
4. Slack App 설정
5. n8n 워크플로우 설계
6. 삽질 포인트 2 — trigger_id 3초 제한
7. 삽질 포인트 3 — JSON body 표현식 문법
8. 삽질 포인트 4 — 모달 제출 후 연결 문제
9. Gemini로 제목 자동 생성
10. 채널 ID를 모달에 담아 전달하기
11. 완성된 결과

---
aliases: VOC 자동화 워크플로우 가이드
작성일: 2026-03-09
수정일: 2026-03-11
상태: 검토
유형: 실무노하우
태그: n8n, slack, notion, jira, automation, voc
발행일:
---

# n8n으로 VOC 수집 자동화 워크플로우 만들기

팀에서 고객 문의를 받는 방식이 통일되어 있지 않으면, 나중에 "그 문의 어디 있어요?"라는 질문이 꼭 나옵니다. 누군가는 Slack 메시지로 공유하고, 누군가는 Notion에 직접 기록하고, 급한 건 구두로 전달됩니다. 수집 자체가 일이 되는 상황입니다.

그렇다고 문의 채널을 통합관리하기엔 현실적으로 어렵습니다. 저희 팀의 경우, 아직은 작은 규모의 서비스임에도 유선, 외부미팅, 채널톡, 서비스와 연결된 google form 등 여러 채널을 통해서 고객 문의가 들어옵니다.

그래서 문의 채널을 통합하는 대신, 서비스 개선 방향 검토 시 분석하기 용이하도록 VoC를 정제해서 수집하는 방법을 해결하고 싶었습니다. Slack에서 `/voc`만 입력하면 폼이 뜨고, 제출하는 순간 Notion에 기록되고, 버그면 Jira 티켓까지 자동으로 만들어지는 흐름으로 계획했습니다. 팀이 이미 활발히 쓰는 Slack에서 시작해서 나머지는 알아서 흘러가는 구조입니다.

이 글은 n8n + Slack + Notion + Jira + Gemini로 그 흐름을 만든 과정을 기록한 것입니다.

---

### 전체를 택배 흐름으로 이해하면 쉽습니다

본격적으로 들어가기 전에 구조를 먼저 이해해두는 게 좋습니다. 노드가 복잡해지면 "지금 이 데이터가 어디서 오는 건지"가 헷갈리기 시작하는데, 그때 전체 그림이 없으면 작은 오류 하나에도 방향을 잃기 쉽습니다.

저를 포함한 PM은 Slack, Notion, Jira 사용에 익숙하지만, n8n은 어색할 수 있습니다. 비유하자면 n8n은 택배 흐름을 만들어 주는 것과 비슷합니다.

보내는 사람(Slack)이 물건을 접수창구(n8n Webhook)에 맡기면, 분류 센터(n8n)가 물건을 뜯어보고 목적지별로 보내는 구조입니다. Notion에도 보내고, 버그면 Jira에도 보내고, 다 처리되면 보낸 사람한테 완료 문자(Slack 알림)를 보내는 것까지 자동으로 됩니다.

```
[Slack] /voc 입력
    → 워크플로우 A (voc-trigger): 모달 열기
    → 사용자가 폼 작성 후 제출
    → 워크플로우 B (voc-submit): 데이터 처리
        → Notion DB 기록
        → (버그 + 높음) → Jira 티켓 생성
        → 채널에 완료 메시지 전송
```

워크플로우가 두 개인 이유는 Slack의 구조 때문입니다. Slack은 슬래시 커맨드 실행과 모달 제출을 서로 다른 URL로 POST합니다. 그래서 n8n에도 Webhook이 두 개 필요합니다. 하나로 합칠 수 없습니다.
참고로 저희는 무료버전을 사용하고 있기에 워크플로우 A를 n8n에서 구현해야 했지만, Slack 유료버전을 사용하고 있다면 워크플로우 A 과정이 필요없습니다. Slack 워크플로우에서 폼을 만들고 Webhook을 실행할 수 있는 유료기능으로 워크플로우 A를 쉽게 대체할 수 있습니다.

---

### 시작 전에 인증 정보 네 가지를 먼저 챙겨두세요

n8n에서 Slack, Notion, Jira를 노드로 연결하려면 각 서비스의 API 토큰이 필요합니다. 중간에 막히지 않으려면 이걸 먼저 발급해두는 게 낫습니다.

| 도구 | 발급 위치 | 비고 |
|---|---|---|
| Slack Bot Token | api.slack.com → OAuth & Permissions | `xoxb-` 로 시작 |
| Notion Integration Token | notion.so/profile/integrations | `secret_` 으로 시작 |
| Jira API Token | id.atlassian.com → Security → API tokens | 이메일 + 토큰 조합 |
| Gemini API Key | Google AI Studio | `AIza` 로 시작 |

Slack, Notion, Jira 토큰은 n8n Credentials에 등록하면 각 노드에서 선택해서 씁니다. Gemini는 n8n 내장 노드가 없어서 HTTP Request로 직접 호출하는데, API Key를 URL 파라미터에 포함시키는 방식입니다. 별도 인증 설정 없이 URL 하나로 끝납니다.

---

### Slack 앱을 먼저 만들어야 합니다

api.slack.com/apps 에서 새 앱을 만듭니다. 저는 이름을 **VoC 수집기**로 했습니다.

설정할 항목은 세 곳입니다. 슬래시 커맨드, Interactivity, Bot Token Scopes입니다.

슬래시 커맨드에서는 `/voc` 커맨드를 만들고 Request URL에 n8n의 첫 번째 Webhook URL(`https://n8n.도메인/webhook/voc-trigger`)을 넣습니다. Interactivity는 ON으로 켜고, Request URL에 두 번째 Webhook URL(`https://n8n.도메인/webhook/voc-submit`)을 넣습니다.

Bot Token Scopes에는 `commands`, `chat:write`, `users:read` 세 가지를 추가합니다. `users:read`는 나중에 제출자 실명을 조회할 때 필요한데, 처음에 빠뜨리면 워크플로우 중간에 권한 오류가 납니다. 미리 추가해두세요.

Slack 메시지 입력창에서 구분하기 쉽게 아이콘도 만들어줬습니다. Gemini에서 무료 버전의 나노바나나로 이미지를 생성했더니 귀엽게 만들어주네요.

앱을 설치하고 Bot Token(`xoxb-...`)을 복사해서 n8n Credentials에 등록하면 Slack 쪽 준비는 끝입니다.

한 가지 더, 실제로 slack에서 봇을 실행할 때에는 봇을 사용할 채널에 `/invite @VoC수집기`로 초대해야 완료 메시지를 보낼 수 있습니다. 이걸 빠뜨리면 나중에 `chat.postMessage`에서 `not_in_channel` 오류가 나면서, Slack으로 응답 메시지를 받을 수 없습니다.

---

### 워크플로우 A: 슬래시 커맨드를 받아 모달을 띄웁니다

워크플로우 설정은 n8n에서 진행합니다.

첫 번째 워크플로우는 단순합니다. Slack에서 `/voc`를 입력하면 폼(모달)이 뜨게 하는 것입니다.

```
Webhook (voc-trigger)
    ↓ Response Mode: Using Respond to Webhook Node
Respond to Webhook → {}
    ↓
HTTP Request → Slack views.open
```

여기서 한 가지 알아야 할 Slack의 규칙이 있습니다. Slack은 슬래시 커맨드를 보내고 3초 안에 응답이 없으면 사용자에게 오류를 보여줍니다. 그런데 모달을 여는 `views.open` 호출이 3초를 넘길 수도 있습니다. 그래서 Webhook을 받자마자 빈 `{}`를 먼저 돌려보내 "받았어요"라고 알려주고, 그 사이에 `views.open`을 호출하는 구조가 됩니다.

이 흐름이 작동하려면 Webhook 노드의 Response Mode를 반드시 **Using Respond to Webhook Node**로 바꿔야 합니다. 기본값으로 두면 Webhook 노드가 즉시 응답해버려서 Respond to Webhook 노드가 무의미해집니다.

`views.open` 호출에서 Body의 핵심은 `trigger_id`와 `private_metadata`입니다.

```json
{
  "trigger_id": "{{$json.body.trigger_id}}",
  "view": {
    "type": "modal",
    "private_metadata": "{{$json.body.channel_id}}",
    "callback_id": "voc_modal",
    "title": { "type": "plain_text", "text": "고객 문의 접수" },
    "submit": { "type": "plain_text", "text": "제출" },
    "close": { "type": "plain_text", "text": "취소" },
    "blocks": [ ... ]
  }
}
```

`private_metadata`에 `channel_id`를 담아두는 이유는, 모달 제출 이후 워크플로우에서 "완료 메시지를 어느 채널로 보낼지" 알기 위해서입니다. 모달이 뜨면 어느 채널에서 실행했는지 정보가 사라지기 때문에, 여기서 미리 챙겨두지 않으면 나중에 꺼낼 방법이 없습니다.

모달에는 고객명(텍스트 입력), 문의 유형(버그/기능 개선/사용 문의/기타), 긴급도(높음/중간/낮음), 문의 내용(리치 텍스트 입력) 네 개 필드를 만들어 줬습니다. 폼의 응답 유형과 수집 내용을 변경하고 싶으면, ChatGPT나 Claude에게 요청하세요. 잘 변경해줍니다.

한 가지 더. `trigger_id`는 슬래시 커맨드 수신 후 3초 이내에만 유효합니다. n8n Test 모드에서 Webhook을 수동 실행하면 이미 만료된 `trigger_id`로 테스트하게 되어 `expired_trigger_id` 오류가 납니다. 설정이 잘못된 줄 알고 한참 뒤졌는데, 워크플로우를 Activate하고 실제 Slack에서 `/voc`를 입력해 테스트하니 바로 됐습니다. Production URL 상태에서 테스트해야 합니다.

---

### 워크플로우 B: 제출된 데이터를 Notion·Jira까지 전달합니다

두 번째 워크플로우엔 Slack 모달에서 제출된 데이터를 받아 Notion에 기록하고, 조건에 따라 Jira 티켓을 만들고, 완료 알림을 보내는 역할을 설정합니다.

```
Webhook (voc-submit)
    ↓
Respond to Webhook → {"response_action": "clear"}
    ↓
Code (payload 파싱)
    ↓
users.info (실명 조회)
    ↓
Gemini (제목 요약)
    ↓
Notion (DB 기록)
    ↓
IF (버그 AND 높음)
    True → Jira → chat.postMessage
    False → chat.postMessage
```

**데이터 꺼내기가 첫 번째 관문입니다**

Slack은 모달 제출 데이터를 `application/x-www-form-urlencoded` 형식으로 보내는데, `payload`라는 필드 하나에 모든 내용을 JSON 문자열로 담아서 옵니다. 첫 번째로 이걸 파싱해야 합니다.

특히 문의 내용 필드를 `rich_text_input`으로 만들었다면 구조가 깊게 중첩되어 있어서, 일반 텍스트 필드처럼 `.value.value`로 바로 꺼낼 수가 없습니다. 처음에 같은 방식으로 파싱했다가 값이 계속 `undefined`로 나왔는데, Slack Block Kit 문서를 뒤져보니 구조가 달랐습니다.

그래서 아래 처럼 모달 제출 데이터를 파싱해서, 파싱한 응답과 `gemini_body`를 담은 json을 반환해주는 Code 노드를 만들어줍니다. 

```javascript
const payload = JSON.parse($input.first().json.body.payload);
const values = payload.view.state.values;

const 문의내용 = values.inquiry_content.value.rich_text_value.elements
  .flatMap(el => el.elements ?? [])
  .map(el => el.elements
    ? el.elements.map(e => e.text).join('')
    : (el.text ?? ''))
  .join('\n');

return [{
  json: {
    고객명: values.customer_name.value.value,
    문의유형: values.inquiry_type.value.selected_option.value,
    긴급도: values.urgency.value.selected_option.value,
    문의내용: 문의내용,
    제출자: payload.user.username,
    제출자_id: payload.user.id,
    제출시각: new Date().toISOString(),
    channel_id: payload.view.private_metadata,
    gemini_body: {
      contents: [{
        parts: [{
          text: "다음 고객 문의 내용을 40자 이내의 한국어 명사형으로 요약해줘. 요약문만 출력하고 다른 말은 하지 마.\n\n" + 문의내용
        }]
      }]
    }
  }
}];
```

`gemini_body`를 여기서 미리 만들어두는 이유는, 이후 Gemini 노드에서 Body를 `{{$json.gemini_body}}`로 바로 참조하기 위해서입니다. 노드가 많아질수록 각 노드에서 이전 노드 참조 경로를 일일이 쓰는 게 번거롭기 때문에, 첫 Code 노드에서 필요한 값을 한 번에 정리해두면 이후가 편합니다.

**제출자 실명을 따로 조회해야 합니다**

Slack의 모달 제출 데이터에는 제출자의 User ID(`U012AB3CD` 형식)만 들어옵니다. Notion의 "보고자" 필드에 ID 대신 실제 이름을 기록하려면 `users.info`로 별도 조회가 필요합니다.

URL은 `https://slack.com/api/users.info?user={{$('Code in JavaScript').first().json.제출자_id}}`로 GET 요청하면 되고, 실명은 응답의 `$json.user.real_name`에 있습니다.

**문의 내용을 Gemini로 요약해서 제목으로 씁니다**

고객 문의를 그대로 Notion 제목이나 Jira Summary로 쓰면 목록에서 한눈에 파악이 안 됩니다. Gemini에 40자 이내 한국어 명사형 요약을 요청해서, `[버그][높음] 결제 완료 후 영수증 미발송 오류` 같은 형식으로 제목을 만들 수 있습니다.

n8n에 Gemini 내장 노드가 없어서 HTTP Request로 직접 호출합니다. URL에 API Key를 파라미터로 포함하는 방식이라 별도 인증 설정은 필요 없습니다.

| 항목 | 값 |
|---|---|
| Method | POST |
| URL | `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=API키` |
| Body | `{{$json.gemini_body}}` (Fixed 모드) |

요약 결과는 `$json.candidates[0].content.parts[0].text`로 꺼냅니다.

**Notion에 기록할 때 Integration 연결을 꼭 확인하세요**

Notion 노드는 내장 노드를 그대로 씁니다. Database Page → Create로 설정하고, 각 필드를 아래처럼 매핑합니다.

| Notion 필드 | 타입 | n8n Expression |
|---|---|---|
| 제목 | Title | `[{{문의유형}}][{{긴급도}}] {{Gemini 요약}}` |
| 고객명 | Text | `{{$('Code in JavaScript').first().json.고객명}}` |
| 문의유형 | Select | `{{$('Code in JavaScript').first().json.문의유형}}` |
| 긴급도 | Select | `{{$('Code in JavaScript').first().json.긴급도}}` |
| 제출시각 | Date | `{{$('Code in JavaScript').first().json.제출시각}}` |
| 보고자 | Select | `{{$('users.info').first().json.user.real_name}}` |

페이지 본문에는 문의 내용 전체를 Paragraph 블록으로 넣습니다.

한 가지 자주 실수하는 부분입니다. n8n Credential에 Notion Token을 등록했어도, Notion DB 자체에 Integration을 연결하지 않으면 접근이 안 됩니다. Notion에서 해당 DB → 우측 상단 `...` → Connections에서 앞서 만든 Integration을 추가해야 합니다. 당연히 됐겠지 하고 넘겼다가 `could not find database` 오류로 돌아옵니다.

**버그이면서 높음일 때만 Jira 티켓을 만듭니다**

IF 노드로 조건을 겁니다. `문의유형 == 버그` AND `긴급도 == 높음`이면 Jira 노드로, 아니면 바로 완료 알림으로 갑니다.

Jira 노드는 내장 노드를 씁니다. Issue Type은 Bug, Priority는 High, Labels에 `urgent`를 넣어두면 Jira 쪽에서도 필터링이 됩니다. Summary는 Gemini가 만들어준 요약문을 그대로 씁니다.

```
Summary: [fix] {{$json.candidates[0].content.parts[0].text}}
```

생성된 티켓 URL은 `https://도메인.atlassian.net/browse/{{$json.key}}` 형식으로 완료 알림 메시지에 포함시킵니다.

**마지막은 채널로 완료 알림을 보냅니다**

두 경로 모두 `chat.postMessage`로 끝납니다. 채널은 앞서 `private_metadata`에 챙겨둔 `channel_id`를 씁니다.

버그+높음이면 Notion 기록 완료와 Jira 링크를 같이 보내고, 그 외에는 Notion 기록 완료만 알립니다.

---

### 완성하고 나면 팀이 쓰는 방식이 바뀝니다

워크플로우가 완성되면 이렇게 됩니다. 팀원이 Slack에서 `/voc`를 입력하면 폼이 뜨고, 제출하는 순간 Notion에 자동으로 기록됩니다. 버그이면서 긴급도가 높으면 Jira 티켓도 자동으로 생기고, 같은 채널에 완료 알림과 Jira 링크가 옵니다.

Notion도, Jira도 직접 열 필요 없이 Slack 하나로 끝납니다. "어디다 기록해요?"라는 질문도 없어집니다.

n8n을 처음 써봤는데 내장 노드가 잘 갖춰져 있어서 Notion·Jira 연동은 생각보다 간단했습니다. Gemini처럼 내장 노드가 없는 경우도 HTTP Request 하나면 충분합니다.

다음에는 여기에 접수된 문의를 유형별로 자동 분류해서 담당자에게 자동 배정하는 흐름을 추가해볼 생각입니다.

---
aliases: 채팅 패널 메시지 스키마
작성일: 2026-05-08
수정일: 2026-05-08
상태: 초안
tags:
  - spec
  - chat-panel
  - schema
관련문서:
  - "[[frd-spec-requirements]]"
  - "[[frd-spec-ai-assistant]]"
  - "[[spec-chat-workflow-control]]"
상위문서: ""
---

# 채팅 패널 메시지 스키마

> 채팅 패널에서 백엔드가 프론트엔드로 전달하는 메시지 구조를 정의한다.
> AI 자유 텍스트와 구조화된 컴포넌트를 어떻게 연결할지를 기술한다.

---

## 1. 구조 원칙

채팅 패널 메시지는 **출처에 따라 책임 주체가 다르다.**

| 출처 | 내용 | 구조화 책임 |
| --- | --- | --- |
| 검증 시스템 (룰베이스 / AI 검증) | ERROR · WARN · INFO 카드, 수정 제안 | **백엔드** — 타입이 있는 JSON 객체로 전달 |
| LLM 대화 응답 | 설명 텍스트, 수정 초안, 요약 | **AI 출력** — 마크다운. 프론트엔드 파서가 인라인 패턴만 업그레이드 |

핵심 원칙:
- **VerificationResult 카드는 AI 텍스트를 파싱해서 만들지 않는다.** 백엔드가 구조화된 객체로 직접 내려준다.
- LLM 자유 텍스트는 마크다운으로 렌더링하되, `#N` · `§조항` · `[버튼]` 인라인 패턴만 컴포넌트로 업그레이드한다.

---

## 2. 메시지 봉투 (Message Envelope)

모든 메시지는 공통 봉투를 공유한다.

```ts
interface ChatMessage {
  id:         string;         // UUID
  role:       "user" | "assistant" | "system";
  created_at: string;         // ISO 8601
  blocks:     MessageBlock[]; // 1개 이상의 블록 배열
}
```

하나의 메시지(`ChatMessage`)는 여러 블록(`MessageBlock`)을 순서대로 담을 수 있다.
예: `[text 블록, verif_result 블록, verif_result 블록, action_prompt 블록]`

---

## 3. MessageBlock 타입 정의

```ts
type MessageBlock =
  | TextBlock
  | VerifResultBlock
  | ActionPromptBlock
  | LegalCiteBlock;
```

---

### 3.1 TextBlock

LLM이 생성한 마크다운 텍스트. 프론트엔드가 마크다운 렌더러를 거쳐 출력한다.

```ts
interface TextBlock {
  type:    "text";
  content: string;   // 마크다운 문자열
}
```

**예시**

```json
{
  "type": "text",
  "content": "전체 **14개 청구항**을 분석했습니다. 총 **3건의 기재불비**가 발견되었습니다.\n\n- **ERROR 1건** — 즉시 수정 필요\n- **WARN 1건** — 수정 권장\n- **INFO 1건** — 참고 사항"
}
```

---

### 3.2 VerifResultBlock

검증 시스템이 생성하는 구조화된 검증 결과. `severity`에 따라 프론트엔드가 색상·아이콘을 자동 적용한다.

```ts
interface VerifResultBlock {
  type:         "verif_result";
  severity:     "error" | "warn" | "info";
  rule_id:      string;         // 검증 항목 ID (예: "CLAIM-007")
  title:        string;         // 항목명 (예: "다중인용항 재인용 금지 위반")
  claim_ref?:   number[];       // 해당 청구항 번호 목록
  legal_basis?: string;         // 법령 표기 (예: "특허법시행령 제5조제6항")
  body:         string;         // 탐지 내용 설명 (마크다운 허용)
  suggestion?:  string;         // 수정 제안 텍스트
}
```

**예시**

```json
{
  "type": "verif_result",
  "severity": "error",
  "rule_id": "CLAIM-007",
  "title": "다중인용항 재인용 금지 위반",
  "claim_ref": [5],
  "legal_basis": "특허법시행령 제5조제6항",
  "body": "청구항 5가 다중인용항인 청구항 3을 재인용하고 있습니다. 다중인용항은 다른 다중인용항의 인용 대상이 될 수 없습니다.",
  "suggestion": "청구항 3의 인용을 단일 항으로 분리하거나, 청구항 5의 인용 구조를 청구항 1 또는 청구항 2로 변경하세요."
}
```

---

### 3.3 ActionPromptBlock

변리사에게 명시적 확인을 요청하는 버튼 묶음. P-5 정책(수정 제안 명시적 반영)을 구현한다.

```ts
interface ActionButton {
  label:     string;
  variant:   "primary" | "outlined" | "ghost";
  action_id: string;   // 백엔드로 콜백할 식별자
  disabled?: boolean;
}

interface ActionPromptBlock {
  type:     "action_prompt";
  question: string;
  actions:  ActionButton[];
}
```

**예시**

```json
{
  "type": "action_prompt",
  "question": "수정 제안을 청구항 5에 반영하시겠습니까?",
  "actions": [
    { "label": "반영",        "variant": "primary",  "action_id": "apply:CLAIM-007:5" },
    { "label": "수정 후 반영", "variant": "outlined", "action_id": "edit:CLAIM-007:5"  },
    { "label": "무시",        "variant": "ghost",    "action_id": "dismiss:CLAIM-007:5" }
  ]
}
```

---

### 3.4 LegalCiteBlock

법령 조문을 독립 블록으로 인용할 때 사용. 인라인 인용은 마크다운 패턴(`§조항`)으로 처리하므로, 이 블록은 심사기준 원문을 별도 강조할 때만 쓴다.

```ts
interface LegalCiteBlock {
  type:    "legal_cite";
  statute: string;   // 법령 표기 (예: "특허법시행령 제5조제6항1호")
  excerpt: string;   // 원문 발췌 (마크다운 허용)
}
```

**예시**

```json
{
  "type": "legal_cite",
  "statute": "특허법시행령 제5조제6항1호",
  "excerpt": "2이상의 청구항을 동시에 인용하는 종속항(다중인용항)은, 다른 다중인용항의 인용 대상이 될 수 없다."
}
```

---

## 4. 블록 → 컴포넌트 렌더링 매핑

```
MessageBlock.type         →  UI 컴포넌트
─────────────────────────────────────────
"text"                    →  <MarkdownBlock>
"verif_result" (error)    →  <VerifCard variant="error">
"verif_result" (warn)     →  <VerifCard variant="warn">
"verif_result" (info)     →  <VerifCard variant="info">
"action_prompt"           →  <ActionPrompt>
"legal_cite"              →  <LegalCiteBlock>
```

**렌더러 의사코드 (React 기준)**

```tsx
function MessageBlockRenderer({ block }: { block: MessageBlock }) {
  switch (block.type) {
    case "text":
      return <MarkdownBlock content={block.content} />;
    case "verif_result":
      return <VerifCard {...block} />;
    case "action_prompt":
      return <ActionPrompt {...block} onAction={handleAction} />;
    case "legal_cite":
      return <LegalCiteBlock {...block} />;
    default:
      return null;
  }
}
```

---

## 5. LLM 출력 패턴 — 파서 렌더링 규약

LLM이 출력하는 텍스트 패턴을 두 종류로 구분한다.

### 5.1 인라인 업그레이드 패턴

기호가 컴포넌트의 일부로 남는다. `TextBlock` 어디서나 적용된다.

| 패턴 | 변환 결과 | 비고 |
| --- | --- | --- |
| `#N` (숫자) | `<ClaimChip>` — 클릭 시 해당 청구항 포커스 | 기호 `#`이 칩 UI의 일부로 표시 |
| `§...조항` | `<LegalCiteChip>` — 인라인 배지 | 기호 `§`이 배지 UI의 일부로 표시 |
| `[버튼명]` (ActionPrompt 내) | `<Button>` | 대괄호는 숨겨지고 버튼으로 변환 |

### 5.2 구조 구분자 — 검증 결과 블록 전용

기호 자체는 렌더링되지 않는다. 파서가 소비한 뒤 숨긴다.

| 구분자 | 위치 | 파싱 결과 | 렌더링 |
| --- | --- | --- | --- |
| ` / ` | 헤더 라인 | `{{등급}}: {{#번호}}` + `{{항목명}}` 으로 분리 | `/` 숨김. `#번호`는 ClaimChip, `항목명`은 텍스트 |
| ` \| ` | 바디 라인 | `{{레이블}}` + `{{내용}}` 으로 분리 | `\|` 숨김. 레이블은 서브텍스트 스타일, 내용은 본문 |
| `---` | 항목 구분 | 블록 경계 | 시각적 구분선 또는 여백으로 처리 |

**헤더 라인 파싱 예시**

```
입력: 거절이유: #5 / 다중인용항 재인용 금지 위반
       ↓ 파싱
등급배지[거절이유]  ClaimChip[#5]  "다중인용항 재인용 금지 위반"
```

**바디 라인 파싱 예시**

```
입력: 근거 | 특허법시행령 제5조제6항
      ↓ 파싱
서브텍스트[근거]  "특허법시행령 제5조제6항"
```

> **`ol` / `ul`과 청구항 번호 참조는 역할이 다르다.**
> - `1. ol` — 범용 순서 목록 (단계, 우선순위 등). 청구항 번호 나열 목적으로 사용 금지.
> - `#N` — 특정 청구항을 참조하는 시맨틱 패턴. ClaimChip으로 렌더링되어 포커스 이동 기능을 갖는다.
> - `인라인 코드` — 조문, 표현식, 키워드 강조용. 청구항 번호 참조에 사용 금지.

**AI 출력 규약** (시스템 프롬프트에 포함할 내용)

```
채팅 패널 출력 규칙:
- 청구항 번호 참조는 항상 #N 형식으로 표기 (예: #5, #14) — ol 번호나 인라인 코드 사용 금지
- ol(1. 2. 3.)은 단계·순서 나열에만 사용. 청구항 번호 목록에 사용 금지
- 법령 인용은 §로 시작 (예: §특허법 제42조제4항제2호)
- h1(# 제목) 사용 금지 — h2(## 제목)만 허용
- HTML 태그 직접 삽입 금지
- 법적 확정 표현 금지 ("등록 가능합니다", "신규성이 있습니다" 등)
- 수정 제안 실행은 반드시 [반영] 버튼을 통해서만 가능하다고 안내
```

---

## 6. 전체 메시지 시퀀스 예시

**시나리오**: 청구항 기재요건 검토 실행 → 결과 표시 → 수정 반영

```json
[
  {
    "id": "msg-001",
    "role": "user",
    "created_at": "2026-05-08T10:24:00Z",
    "blocks": [
      { "type": "text", "content": "청구항 기재요건 검토를 시작해주세요." }
    ]
  },
  {
    "id": "msg-002",
    "role": "assistant",
    "created_at": "2026-05-08T10:24:05Z",
    "blocks": [
      {
        "type": "text",
        "content": "## 검토 결과 요약\n\n전체 **14개 청구항**을 분석했습니다. **3건**의 기재불비가 발견되었습니다.\n\n- **ERROR 1건** — 즉시 수정 필요 (거절이유)\n- **WARN 1건** — 수정 권장\n- **INFO 1건** — 참고 사항"
      },
      {
        "type": "verif_result",
        "severity": "error",
        "rule_id": "CLAIM-007",
        "title": "다중인용항 재인용 금지 위반",
        "claim_ref": [5],
        "legal_basis": "특허법시행령 제5조제6항",
        "body": "청구항 #5가 다중인용항인 청구항 #3을 재인용하고 있습니다.",
        "suggestion": "청구항 #3의 인용을 단일 항으로 분리하거나, 청구항 #5의 인용 구조를 청구항 #1 또는 #2로 변경하세요."
      },
      {
        "type": "verif_result",
        "severity": "warn",
        "rule_id": "CLAIM-014",
        "title": "임의부가적 표현 사용",
        "claim_ref": [14],
        "legal_basis": "특허법 제42조제4항제2호",
        "body": "청구항 #14에서 `「필요에 따라」` 표현이 발견되었습니다.",
        "suggestion": "해당 표현을 삭제하거나, 발명의 설명에 선택적 첨가 근거를 명확히 보완하세요."
      },
      {
        "type": "verif_result",
        "severity": "info",
        "rule_id": "CLAIM-006",
        "title": "명확성 목적 동시인용",
        "claim_ref": [6],
        "legal_basis": "시행령 제5조제5항1호②",
        "body": "거절이유에 해당하지 않으나, 청구항 #6에서 명확성 목적의 동시인용이 확인되었습니다."
      },
      {
        "type": "action_prompt",
        "question": "ERROR 항목(청구항 #5)의 수정 초안을 생성하시겠습니까?",
        "actions": [
          { "label": "수정 초안 생성", "variant": "primary",  "action_id": "draft:CLAIM-007:5" },
          { "label": "나중에",         "variant": "ghost",    "action_id": "defer:CLAIM-007:5" }
        ]
      }
    ]
  },
  {
    "id": "msg-003",
    "role": "user",
    "created_at": "2026-05-08T10:24:18Z",
    "blocks": [
      { "type": "text", "content": "청구항 5의 수정 초안을 보여줘." }
    ]
  },
  {
    "id": "msg-004",
    "role": "assistant",
    "created_at": "2026-05-08T10:24:22Z",
    "blocks": [
      {
        "type": "text",
        "content": "## 수정 초안 — 청구항 #5\n\n인용 대상을 단일 항으로 변경했습니다.\n\n```\n【청구항 5】\n청구항 1에 있어서,\n상기 폴리머 조성물은 점도가 100~500 mPa·s인\n것을 특징으로 하는 발광 소자.\n```"
      },
      {
        "type": "action_prompt",
        "question": "이 수정안을 청구항 5에 반영하시겠습니까?",
        "actions": [
          { "label": "반영",         "variant": "primary",  "action_id": "apply:CLAIM-007:5" },
          { "label": "수정 후 반영", "variant": "outlined", "action_id": "edit:CLAIM-007:5"  },
          { "label": "무시",         "variant": "ghost",    "action_id": "dismiss:CLAIM-007:5" }
        ]
      }
    ]
  }
]
```

---

## 7. 미결 사항

- [ ] `action_id` 콜백 처리 방식 — REST vs WebSocket vs SSE 중 결정 필요
- [ ] 스트리밍 응답 시 블록 단위 청크 전송 방식 (TextBlock은 스트리밍, VerifResultBlock은 완성 후 전송)
- [ ] `claim_ref` 클릭 시 청구항 패널 포커스 이동 — 이벤트 버스 설계 필요
- [ ] 검증 결과 재실행 시 기존 `verif_result` 블록 업데이트 vs 새 메시지 추가 정책

# 디자인 토큰 점검 체크리스트

> 소스: `design-token-schema.draft.json`  
> 작성: 2026-04-28

---

## Phase 1 — 미결 확인 항목 (Figma에서 직접 확인)

- [ ] **#1 Primary 색상 기준 확정**  
  현재 서비스 `#3361BE` vs Figma `primary/500 #3b5ccd` 중 기준값 결정.  
  결정 후 `primitive.color.primary.500` 및 semantic 전체에 반영.

- [ ] **#2 text.primary / text.secondary color-bk 단계 확인**  
  현재 스키마: `text.primary → color-bk/900`, `text.secondary → color-bk/500`.  
  실제 Figma 컴포넌트와 대조하여 단계 확정.

- [ ] **#3 radius md / pill 실제 값 확인**  
  `semantic.radius.md`, `radius.pill`이 Figma variables에 없음.  
  버튼·카드·모달 컴포넌트에서 `border-radius` 직접 측정.

- [ ] **#4 shadow.button 실제 값 확인**  
  `semantic.shadow.button`이 Figma variables에 없음.  
  버튼 컴포넌트의 `box-shadow` 값(offset-x, offset-y, blur, spread, color) 확인.

---

## Phase 2 — 스키마 완성 (Phase 1 완료 후)

- [ ] **#5 semantic 토큰 value null 전체 resolve**  
  아래 전 항목의 `value: null`을 primitive 값으로 채우기.
  - `color.text` (primary / secondary / subtle / disabled / inverse / accent / danger)
  - `color.background` (canvas / surface / elevated / accent / disabled / danger)
  - `color.border` (default / subtle / strong / accent / danger)
  - `color.button.primary`, `color.button.outlined`
  - `color.status` (success / info / warning / danger)
  - `spacing` (xs / sm / md / lg / xl)
  - `radius` (sm / md / lg / pill)
  - `shadow.button`

---

## Phase 3 — 자동화 구축

- [ ] **#6 Figma Variables API 추출 스크립트 작성**  
  `GET /v1/files/:key/variables/local`로 변수 추출 → 스키마 형식 변환.  
  Figma Access Token 필요. Phase 1~2와 독립적으로 진행 가능.

- [ ] **#7 토큰 → 플랫폼 변환기 작성** *(#5 완료 후)*  
  완성된 JSON → 각 플랫폼 형식으로 변환.
  - CSS Variables: `--color-text-primary: #090909`
  - Tailwind: `theme.extend.colors`
  - MUI: `createTheme` 형식

---

## 진행 순서 요약

```
#1 Primary 색상 확정 ─┐
#2 color-bk 단계 확인 ─┤ → #5 semantic resolve → #7 변환기
#3 radius 값 확인 ─────┤
#4 shadow 값 확인 ─────┘

#6 Figma API 스크립트 (독립 진행)
```

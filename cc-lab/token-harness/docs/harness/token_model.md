# 토큰 모델 · 정규화

## SSOT 로드
- `src/load.ts`가 `tsx`로 `../designTokens-v0.2.ts`의 `default export`(평가된 객체)를 import한다. 빌드 스텝 없음.
- 구조: `{ color, typography, spacing, radius, shadow, theme }`.

## 정규화 (`src/normalize.ts`)
재귀로 모든 leaf를 한 행으로 펼친다.

```
TokenLeaf = {
  path:  string        // 점 경로, 예: "color.text.muted"
  value: string|number // 평가된 최종 값
  type:  "color"|"dimension"|"shadow"|"fontFamily"|"fontWeight"|"number"|"other"
  group: string        // color 토큰은 color 다음 세그먼트(primitive/brand/text/...), 그 외 top-level
  refOf: string|null   // 값-기반 추적: 이 색이 primitive hex와 일치하면 그 primitive 경로, 아니면 null
}
```

### 타입 판정
- `#`/`rgb`/`rgba`로 시작 → `color`
- `…px` → `dimension`
- `0 …`·`rgba(` 포함 + 다중 값(shadow 그룹) → `shadow`
- `Pretendard` 등 폰트명 → `fontFamily`, 숫자 → `fontWeight`/`number`

### refOf (값-기반 참조 추적)
- `color.primitive.*`와 `color.brand.*`의 hex를 정규화(소문자, `culori.formatHex`)해 **역색인** `hex → [primitive 경로…]`를 만든다.
- 각 semantic color leaf의 값이 역색인에 있으면 `refOf = 첫 일치 경로`, 없으면 `refOf = null`(= 하드코딩).
- ts-morph 없이 값 기준으로 추적한다. "이 값이 primitive로 존재하는가"가 곧 하드코딩 판정 근거이므로 충분하다.

## 산출
- `dist/tokens.normalized.json` : `{ leaves: TokenLeaf[], byPath: Record<path,value> }`.
- 이후 모든 검증·산출·동기화는 이 정규화 결과(또는 `byPath`)를 입력으로 받는다.

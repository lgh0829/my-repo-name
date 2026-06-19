# 산출물 생성 형식

`build`는 내부적으로 `lint`를 선행하고, **error 0일 때만** 생성한다. 모든 산출물 상단에 "생성됨 · 직접 수정 금지" 배너를 넣는다.

## Tailwind (`src/emit/tailwind.ts` → `dist/tailwind.tokens.ts`)
`theme.extend` 조각을 export한다.
- `colors`: `colorTokens`의 중첩 구조 유지(primitive + semantic). 배열(차트 시퀀스)은 인덱스 키 객체로.
- `spacing`: `spacingTokens` 그대로(px 문자열).
- `borderRadius`: `radiusTokens`.
- `boxShadow`: `shadowTokens`.
- `fontFamily`: `{ sans: ["Pretendard", ...] }`.
- `fontWeight`: `typographyTokens.fontWeight`.

```ts
export const patsolTheme = { extend: { colors: {...}, spacing: {...}, ... } } as const;
```

## MUI (`src/emit/mui.ts` → `dist/mui.theme.ts`)
`themeModeTokens.light` / `themeModeTokens.dark`를 그대로 매핑해 `createTheme` 2개를 export한다.
- `palette`: themeModeTokens 값
- `typography.fontFamily`: `Pretendard`
- `shape.borderRadius`: `radiusTokens.md`의 px 수치
- 추가 시맨틱이 필요하면 `colorTokens`에서 보강

```ts
export const lightTheme = createTheme({ palette: {...}, typography: {...}, shape: {...} });
export const darkTheme  = createTheme({ ... });
```

> dark semantic이 빈약하면(themeModeTokens.dark가 일부 primitive 재사용 수준) 현 상태대로 내고 `report.md`에 "dark semantic 부재"를 표기한다.

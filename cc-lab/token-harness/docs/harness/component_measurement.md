# 컴포넌트 색상 실측 · 개선 제안

실측은 **비결정적**(로그인·A/B·동적 렌더)이므로 `lint` 게이트와 분리한다. 결과는 `dist/measured.json` 캐시로만 합류한다. HTML PoC 파일은 사용하지 않는다.

## 측정 대상 정의 (`src/measure/pairs.ts`)
컴포넌트 → 기대 토큰 매핑. 각 항목:
```
{ component, selector|nodeId, expects: { color?, background?, border? }, props: [...] }
```
초기 대상: primary 버튼, danger 버튼, 강조 칩, 차트 범례, topic 배지, 헤더/카드 표면.

## 라이브 실측 (`src/measure/live.ts`) — 수동 트리거
- 브라우저 MCP(`mcp__Claude_in_Chrome__*` 또는 `mcp__Claude_Preview__*`)로 patsol.kr 진입.
- 대상 엘리먼트에서 `getComputedStyle`로 `color/backgroundColor/borderColor/boxShadow/borderRadius` 수집(체크리스트 #3 radius·#4 shadow 실측 동시 해결).
- 로그인/동적 화면은 사람이 화면을 띄운 뒤 수집한다. 결과를 `dist/measured.json`의 `live` 항목에 기록.

## Figma 노드 실측 (`src/measure/figma.ts`)
- Figma Dev Mode MCP `get_variable_defs` / `get_design_context`, 또는 REST `view_node`로 노드 fill/stroke/effect 추출.
- 결과를 `dist/measured.json`의 `figma` 항목에 기록.

## 제안 (`src/measure/suggest.ts`)
- 측정 색 → `differenceCiede2000`로 가장 가까운 토큰 산출.
- 리포트에 **3열 대조**: `디자인 의도(Figma)` vs `실제 구현(라이브)` vs `권장 토큰`.
- 대비 미달 시 동일 hue·명도만 보정한 후보를 제시(WCAG 통과 보장).

## 캐시 포맷 (`dist/measured.json`)
```
{ "live":  { "<component>": { "color": "#..", "background": "#..", "border": "#..", "borderRadius": "..", "boxShadow": ".." } },
  "figma": { "<component>": { "fill": "#..", "stroke": "#.." } } }
```
파일이 없으면 `report`는 정적 검증만 출력한다.

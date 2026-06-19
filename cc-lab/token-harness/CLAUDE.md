# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

이 저장소는 PatSol(특허 SaaS, https://patsol.kr/home) 디자인 토큰을 단일 진실원천(SSOT)으로 관리하고, 토큰을 검증·리포트하고, Tailwind·MUI 산출물을 생성하며, Figma 변수와 동기화하는 **디자인 토큰 하네스**다.

이 파일은 **항상 읽히는 얇은 하네스**다. 세부 규칙은 작업 유형에 맞춰 `docs/harness/*.md`를 추가로 읽는다.

---

## 절대 규칙

- **SSOT는 `./designTokens-v0.2.ts`(하네스 루트) 하나다.** 토큰 값은 이 파일에서만 편집한다. `dist/*`는 전부 생성 산출물이므로 직접 수정하지 않는다. (2026-06: design/에서 cc-lab/token-harness/로 이동, 자립 구조.)
- **브랜드 키 컬러(primary)는 `#3361BE`로 확정.** 브랜드톤 검증의 기준 hue이며, 변경은 디자이너 합의 후에만 한다.
- **HTML PoC 파일(cc-workspace 내 `*.html`)은 열람·참조 금지.** 인터랙션 흐름 PoC 결과물이며 토큰 근거로 쓰지 않는다.
- **컴포넌트 색상 실측은 라이브 서비스(patsol.kr) 또는 Figma 노드에서만 한다.** 실측 결과는 `dist/measured.json` 캐시로 분리하고, 비결정적이므로 `lint` 게이트에 포함하지 않는다.
- **명도 역전(gray650>gray700, gray590>gray595)은 "의도된 역할 분리"로 간주(예외 등록, info).** 값 변경은 디자이너 확정 후에만 한다.
- **Figma 토큰을 끌어올 때 발급 키/토큰을 코드·리포트·로그에 노출하지 않는다.** 환경변수로만 주입한다.

---

## 작업 시작 체크

작업 시작 전 아래를 확인한다.

- 작업 유형: 토큰 검증 / 컴포넌트 색상 제안 / 산출물 생성 / Figma 동기화
- SSOT 버전: `designTokens-v0.2.ts` (현행) — 구버전 `designTokens.ts`는 참조만, 편집 금지
- 산출 타깃: Tailwind `theme.extend` / MUI `createTheme` (CSS 변수는 범위 외)
- 실측 소스 필요 여부: 라이브(patsol.kr) / Figma 노드 / 둘 다
- Figma 접근 경로: `FIGMA_API_KEY` REST API / Figma Dev Mode MCP(`get_variable_defs`) 중 가용한 것

---

## 참조 문서 라우팅

필요한 세부 문서만 읽는다.

| 작업 | 먼저 읽을 문서 |
|---|---|
| 토큰 모델·정규화·SSOT 파싱 규칙 | `docs/harness/token_model.md` |
| 검증 규칙(대비·중복·역전·하드코딩·네이밍·브랜드톤) 판정 로직 | `docs/harness/validation_rules.md` |
| 컴포넌트 색상 실측(라이브/Figma)·개선 제안 | `docs/harness/component_measurement.md` |
| Tailwind·MUI 산출물 생성 형식 | `docs/harness/emit_targets.md` |
| Figma 변수 동기화(REST/Dev Mode MCP) | `docs/harness/figma_sync.md` |
| 임계값·페어·예외 변경, 하네스 유지보수 | `docs/harness/harness_maintenance.md` |

원본 토큰 점검 이력이 필요하면 `../../design/design-token-checklist.md`를 확인한다.

---

## CLI 빠른 사용

```bash
npm install              # 최초 1회
npm run tokens normalize # SSOT → dist/tokens.normalized.json
npm run tokens lint      # 검증 → dist/report.json, error≥1이면 exit 1 (CI 게이트)
npm run tokens report    # findings + measured → dist/report.md
npm run tokens build     # lint 선행 → dist/tailwind.tokens.ts, dist/mui.theme.ts
npm run tokens all       # normalize → lint → report → build 일괄

# opt-in (수동 트리거, lint 게이트와 분리)
npm run tokens measure     # dist/measured.json 소비 → 3열 대조 제안
npm run tokens sync        # FIGMA_API_KEY(REST·Enterprise 전용) → 변수 diff
npm run tokens nodes       # config/figma-nodes.txt 파싱 → 노드 목록(Dev Mode MCP 대상)
npm run tokens figma-diff  # dist/figma-vars.json(MCP 추출) ↔ SSOT 대조 → figma-diff.md
npm run tokens svg         # 토큰 전체를 SVG 스펙시트로 → dist/tokens-figma.svg (Figma에 붙여넣기용)
npm run tokens audit-product [src경로]  # 제품 소스 하드코딩 hex ↔ SSOT 대조 → product-color-audit.md (매핑표+파일별 치환계획). 기본 PatSol-Front/src
```

> Figma 변수 추출 기본 경로는 **Dev Mode MCP 노드 방식**이다(REST `variables/local`은 Enterprise 전용).
> `config/figma-nodes.txt`에 노드 URL을 채우고 `nodes` → MCP `get_variable_defs` → `figma-diff` 순으로 진행한다.
> 상세는 `docs/harness/figma_sync.md`.

---

## 산출물 위치

- 정규화 토큰: `dist/tokens.normalized.json`
- 검증 결과: `dist/report.json` (기계용), `dist/report.md` (사람용)
- 실측 캐시: `dist/measured.json`
- 플랫폼 산출물: `dist/tailwind.tokens.ts`, `dist/mui.theme.ts`
- 회귀 픽스처: `fixtures/known-issues.json`
- 설정(임계값·페어·예외·브랜드 기준): `config/harness.config.ts`

---

## 작업 종료 체크

작업 중 대비 임계값, 검증 페어, 예외 allowlist, 브랜드 기준값, 산출물 형식, 실측 매핑이 바뀌었으면 `docs/harness/harness_maintenance.md`를 읽고 하네스(설정·문서) 반영 후보를 사용자에게 제안한다.

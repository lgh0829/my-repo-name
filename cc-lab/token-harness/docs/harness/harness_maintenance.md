# 하네스 유지보수

작업 중 아래가 바뀌면 설정/문서/픽스처에 반영하고 사용자에게 제안한다.

## 변경 감지 → 반영 위치
| 바뀐 것 | 반영 위치 |
|---|---|
| 대비 임계값(4.5/3.0) | `config/harness.config.ts` `contrast.thresholds` |
| 검사할 fg/bg 페어 | `config/harness.config.ts` `pairs` |
| 명도 역전 예외 쌍 | `config/harness.config.ts` `lightnessExceptions` |
| 브랜드 기준 hex / hue 밴드 | `config/harness.config.ts` `brand` (현재 `#3361BE`) |
| primitive 네이밍 allowlist | `config/harness.config.ts` `namingAllowlist` |
| 하드코딩 severity 분류 | `config/harness.config.ts` `hardcoded.severityByGroup` |
| 컴포넌트→토큰 매핑 | `src/measure/pairs.ts` |
| Figma 컬렉션 매핑 | `config/harness.config.ts` `figmaMap` |
| 산출물 형식 | `src/emit/*.ts` + `docs/harness/emit_targets.md` |

## 회귀 픽스처
- `fixtures/known-issues.json`은 "현재 알려진 결함"의 기대 스냅샷이다.
- 토큰을 의도적으로 고쳤으면 `lint` 결과와 비교해 픽스처를 갱신한다.
- 새 error/warn이 픽스처에 없으면 회귀이므로 원인을 먼저 확인한다.

## 미결 정책 (사람 결정 필요)
- 명도 역전: 값 유지(역할 분리) vs 수정 — 디자이너 확정.
- landing/event 일회성 hex: "마케팅 예외 네임스페이스"로 분리해 severity 완화할지.
- dark semantic 부재: dark 전용 semantic 토큰 정의 여부.
- primary 기준: `#3361BE` 확정(코드 현행). Figma `#3b5ccd`와의 통일은 sync diff 확인 후 결정.

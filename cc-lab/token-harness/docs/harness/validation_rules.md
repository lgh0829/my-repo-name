# 검증 규칙 판정 로직

각 규칙 `(model, config) => Finding[]`. `Finding = { rule, severity: "error"|"warn"|"info", path, message, data? }`.
`lint`은 `error ≥ 1`이면 exit 1 (CI 게이트). `warn`/`info`는 게이트를 막지 않는다.

## 1. contrast (`validators/contrast.ts`)
- `config.pairs`의 의미적 fg/bg 쌍만 검사한다. 토큰 전수 조합 금지(무의미 페어 폭발 방지).
- `culori.wcagContrast(fg, bg)` 비율 계산.
  - 일반 텍스트 < **4.5** → error
  - 큰 텍스트/UI 요소(`large:true`) < **3.0** → warn
- `topic.objective`/`topic.solution`/`info`처럼 bg+text가 한 그룹인 경우 config에 명시 페어로 포함.

## 2. duplicate-hex (`validators/duplicate-hex.ts`)
- 모든 color leaf를 `formatHex`로 정규화 후 그룹핑.
- **primitive 레이어 내부에서** 같은 hex가 2개 이상 이름으로 존재 → warn (예: `blue100`=`chartBlue50`=`#EBF0FA`).
- semantic이 동일 primitive를 가리키는 것은 정상 → 신고하지 않음.

## 3. lightness-monotonic (`validators/lightness-monotonic.ts`)
- `gray(\d+)` 네이밍을 숫자로 정렬. 숫자가 클수록 어두워야 한다(oklch `l` 단조 감소).
- `culori` oklch 변환으로 `l` 비교. 연속 쌍에서 큰 숫자가 더 밝으면 역전.
- `config.lightnessExceptions`에 등록된 쌍(`gray650/gray700`, `gray590/gray595`)은 **info로 강등**. 신규 역전만 **error**.
- `grayWarm`/`grayCool`은 순수 스케일에서 분리됨 → 검사 제외.

## 4. hardcoded-hex (`validators/hardcoded-hex.ts`)
- `group != primitive && type == color && refOf == null` → 하드코딩.
- severity: 코어 semantic(`text/background/border/icon/action/metric`) → **error**, 마케팅/일회성(`landing/event`) → **warn**, 컨텍스트(`topic/status/info/overlay/highlight`) → **warn**.
- 제안: 가장 가까운 primitive를 ΔE2000(`differenceCiede2000`)로 찾아 `ΔE < 2`면 "해당 primitive로 교체", 아니면 "primitive 신규 등록 후 참조" 권고. `data`에 후보·ΔE 기록.

## 5. naming (`validators/naming.ts`)
- primitive 이름: `^[a-z]+[0-9]{2,3}$`(스케일) 또는 `config.namingAllowlist`(의미명: white/black/danger/grayWarm 등)에 포함 → 통과. 아니면 warn.
- 자동 수정 불가(사람 판단) → 항상 warn.

## 6. brand-tone (`validators/brand-tone.ts`)
- 기준 `config.brand.keyHex` = `#3361BE`의 oklch hue.
- "브랜드 블루여야 하는" 경로(`config.brandExpectedMatch`: 경로에 `accent` 포함, `chart.blueScale.*`)가 hue 밴드(±`hueBand`°) 밖 또는 chroma < 하한 → warn.
- danger/success/warning, `chart.trendSequence`, `landing.*`, `topic.*`는 의도적 다색 → 제외.

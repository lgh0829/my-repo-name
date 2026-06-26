/**
 * 하네스 설정 — 임계값·페어·예외·브랜드 기준이 모이는 단일 지점.
 * 미결 정책 변경은 여기서 한다. (docs/harness/harness_maintenance.md 참조)
 */

export interface ContrastPair {
	fg: string; // 토큰 경로 또는 hex
	bg: string;
	label: string;
	large?: boolean; // 큰 텍스트/UI 요소면 3.0 기준
}

export const harnessConfig = {
	/** 브랜드 키 컬러 — 코드 현행 확정값. 브랜드톤 검증 기준 hue. */
	brand: {
		keyHex: "#3361BE",
		hueBand: 25, // oklch hue ± (deg)
		minChroma: 0.04, // 무채색에 가까우면 블루로 보지 않음
	},

	contrast: {
		normalText: 4.5,
		largeText: 3.0,
	},

	/** 의미적으로 함께 쓰이는 fg/bg 쌍만 검사한다. */
	pairs: [
		{ fg: "color.text.primary", bg: "color.background.canvas", label: "본문 기본 텍스트" },
		{ fg: "color.text.secondary", bg: "color.background.canvas", label: "보조 텍스트" },
		{ fg: "color.text.muted", bg: "color.background.canvas", label: "muted 텍스트" },
		{ fg: "color.text.helper", bg: "color.background.canvas", label: "helper 텍스트" },
		{ fg: "color.text.disabled", bg: "color.background.canvas", label: "disabled 텍스트", large: true },
		{ fg: "color.text.inverse", bg: "color.background.inverse", label: "반전 텍스트" },
		{ fg: "color.text.inverse", bg: "color.background.danger", label: "danger 버튼 텍스트", large: true }, // 버튼 라벨=UI/Large → 3.0 기준
		{ fg: "color.text.inverse", bg: "color.brand.primary", label: "primary 버튼 텍스트" },
		{ fg: "color.text.accent", bg: "color.background.canvas", label: "accent 링크 텍스트" },
		{ fg: "color.text.accent", bg: "color.background.accentSoft", label: "accent on soft bg" },
		{ fg: "color.text.primary", bg: "color.background.surface", label: "surface 위 본문" },
		{ fg: "color.text.primary", bg: "color.background.selected", label: "선택 행 본문" },
		{ fg: "color.topic.objective.text", bg: "color.topic.objective.background", label: "objective 배지" },
		{ fg: "color.topic.solution.text", bg: "color.topic.solution.background", label: "solution 배지" },
		{ fg: "color.text.info", bg: "color.background.info", label: "info 배너" },
	] as ContrastPair[],

	/** 명도 역전 예외 — v0.3 ramp 정리로 역전 구간 제거됨. 예외 없음. */
	lightnessExceptions: [] as [string, string][],

	/** 순수 gray 스케일에서 분리된 의미색 — v0.3에서 grayWarm/grayCool 폐기됨. v0.5에서 grayDisabled도 gray300으로 ramp 편입. */
	lightnessExcludeNames: [] as string[],

	/** primitive 네이밍 allowlist (스케일 패턴 외 허용 의미명). */
	namingAllowlist: [
		"white", "black", "blackA20", "blackA40", "whiteA50",
		"eventBannerStart", "eventBannerEnd", "eventButtonHover",
		"excelGreen", "metricLowGreen",
	],

	hardcoded: {
		/** group별 severity. 미지정 그룹은 warn. */
		severityByGroup: {
			text: "error", background: "error", border: "error",
			icon: "error", action: "error", metric: "error",
			landing: "warn", event: "warn",
			topic: "warn", status: "warn", info: "warn",
			overlay: "info", highlight: "warn", chart: "warn",
		} as Record<string, "error" | "warn" | "info">,
		nearPrimitiveDeltaE: 2, // ΔE < 2면 기존 primitive 교체 권고
	},

	/** 브랜드 블루여야 하는 경로 판정(부분 일치/접두). */
	brandExpectedMatch: {
		includes: ["accent"], // 경로에 'accent' 포함
		prefixes: ["color.chart.blueScale"],
		// 의도적 다색 — 제외
		excludePrefixes: ["color.chart.trendSequence", "color.landing", "color.topic"],
	},

	/** Figma 변수명 ↔ 코드 토큰 경로 매핑 (네이밍 체계가 달라 이름 자동매칭 불가 → 명시 매핑). */
	figmaMap: {
		"color/primary/500": "color.brand.primary",
		"main-color/500": "color.brand.primary",
		"main primary": "color.brand.primary",
		"color/color-wh": "color.primitive.white",
		"Black": "color.primitive.gray900",
		"color/color-gray/700": "color.primitive.gray450",
		"color/info-color/500": "color.action.info",
	} as Record<string, string>,

	/** 값 기반 판정 임계값(ΔE). */
	figmaDiff: { near: 2, similar: 8 },

	/** audit-product 제외 파일 (srcDir 기준 상대경로 suffix 일치). 비핵심 화면(우림 파트너/관리자 전용 등). */
	auditExclude: [
		"pages/Urim.tsx",
		"pages/UrimAdmin.tsx",
	],
} as const;

export type HarnessConfig = typeof harnessConfig;
export default harnessConfig;

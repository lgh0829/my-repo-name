/**
 * @file 디자인 토큰 정의
 * @description MUI 테마와 Tailwind 설정에서 함께 참조할 스타일 기준값을 관리합니다.
 * @author yunjulee
 * @version 0.2
 * @lastModified 2026-05-13
 *
 * --- v0.2 변경 내역 ---
 * [제거] gray100 (#F5F5F5) — 미참조 확인 후 삭제
 * [제거] gray450 (#DDDDDD) — 미참조 확인 후 삭제
 * [이름변경] gray580 → grayWarm : 순수 gray가 아닌 warm tint (#72777A), text.label에 사용
 * [이름변경] gray605 → grayCool : 순수 gray가 아닌 cool tint (#595D62), text.detail에 사용
 * [문서화] 명도 역전 구간 주석 추가 (값은 유지 — UI 영향 없이 수정하려면 디자이너 확인 필요)
 *   · gray650(#5E5E5E) > gray700(#616161) : gray700이 실제로 더 밝음
 *   · gray590(#666666) > gray595(#777777) : gray595가 실제로 더 밝음
 */

const primitiveColors = {
	white: "#FFFFFF",
	black: "#000000",

	// --- Blue ---
	blue50:  "#F3F6FC",
	blue100: "#EBF0FA",
	blue300: "#A3BCE8",
	blue500: "#3361BE",

	// --- Chart Blue ---
	chartBlue50:  "#EBF0FA",
	chartBlue100: "#CBD7F1",
	chartBlue200: "#A3B9E6",
	chartBlue300: "#7A9ADB",
	chartBlue400: "#527CD1",
	chartBlue800: "#284C95",
	chartBlue900: "#1D376D",

	// --- Info ---
	infoText: "#014361",

	// --- Gray Scale ---
	// 숫자가 클수록 어두운 색이 원칙이나, 일부 구간 역전이 존재합니다.
	// 역전 구간은 아래 주석으로 표기합니다. 수정 시 실제 UI 영향을 확인하세요.
	gray50:  "#FAFAFA",
	// gray100 (#F5F5F5) 제거 — v0.2: 미참조
	gray200: "#EDEDED",
	// gray250 (#EEEEEE) 제거 — v0.2 정리: gray200과 ΔE<1 near-dup이자 스케일 역전(250>200인데 더 밝음).
	//   유일 참조였던 border.light를 gray200으로 통합.
	gray300: "#E0E0E0",
	gray400: "#D9D9D9",
	gray425: "#CCCCCC",
	// gray450 (#DDDDDD) 제거 — v0.2: 미참조
	gray500: "#BDBDBD",
	gray525: "#AAAAAA",
	gray550: "#9E9E9E",
	gray575: "#888888",
	/** warm tint (#72777A). 순수 gray 스케일에서 분리 — text.label 전용 */
	grayWarm: "#72777A",
	/** ⚠ 역전: gray590(#666666)보다 gray595(#777777)가 실제로 더 밝습니다.
	 *  text.panel(darker)과 text.dim(lighter)의 역할 분리가 의도된 경우 값은 유지합니다. */
	gray590: "#666666",
	gray595: "#777777",
	gray600: "#757575",
	/** cool tint (#595D62). 순수 gray 스케일에서 분리 — text.detail 전용 */
	grayCool: "#595D62",
	/** ⚠ 역전: gray650(#5E5E5E)보다 gray700(#616161)이 실제로 더 밝습니다.
	 *  text.readonly(darker)와 text.muted(lighter)의 역할 분리가 의도된 경우 값은 유지합니다. */
	gray650: "#5E5E5E",
	gray700: "#616161",
	gray750: "#494949",
	gray800: "#424242",
	gray850: "#212121",
	gray900: "#1E1E1E",

	// --- Neutral (dark mode / strong backgrounds) ---
	neutral700: "#333333",
	neutral900: "#171717",
	neutral950: "#111111",

	// --- Red / Danger ---
	// scale이 아니라 UI 사용 맥락(기본·인터랙션·hover) 기준으로 분리합니다.
	danger:             "#FF3232",
	dangerAction:       "#F54848",
	dangerActionHover:  "#E55648",
	errorAccent:        "#FD6051",
	metricDanger:       "#FB2828",
	iconDanger:         "#EF4444",
	dangerOutline:      "#EF3535",

	// --- Success / Warning ---
	success300: "#7DDE86",
	success500: "#22C55E",
	warning500: "#FFAB03",
	warning100: "#FFE4B5",

	// --- Action / Metric greens (semantic 직박힘 정리: primitive 경유) ---
	excelGreen:     "#6EB92C", // action.excel 전용 (Excel 내보내기 버튼)
	metricLowGreen: "#22CC00", // metric.low 전용 (낮음 지표)

	// --- Special / Context-specific ---
	selectedBackground:   "#EBEFF8",
	subtleBackground:     "#F5F5F5", // v0.2 정리: #F4F4F4→#F5F5F5 통일(제품 #f5f5f5·#f4f4f4 수렴, ΔE0.2)
	accentSoftBackground: "#E8F0FE",
	accentChipBackground: "#EEF2FF",
	researchTabBackground:"#EDF2FF",
	summaryTableAccent:   "#D7E1F5",
	timelineAccent:       "#1976D2",
	researchSelected:     "#2F55A3",

	// --- Event / Marketing ---
	eventBannerStart: "#6FC6F1",
	eventBannerEnd:   "#483EBF",
	eventButtonHover: "#F5FAFF",

	// --- Chart: Trend ---
	trendMint100:   "#C6E3CB",
	trendCyan200:   "#83CACF",
	trendSky300:    "#47AED0",
	trendBlue400:   "#3984B6",
	trendBlue500:   "#2C5A9C",
	trendIndigo600: "#1E3082",
	trendNavy700:   "#141C59",
} as const;

const brandTokens = {
	/**
	 * PatSol 서비스 키 컬러입니다.
	 * Primary CTA, 브랜드 강조, 주요 사용자 액션에 사용합니다.
	 */
	primary: primitiveColors.blue500,
} as const;

const chartBlueScale = {
	900: primitiveColors.chartBlue900,
	800: primitiveColors.chartBlue800,
	500: brandTokens.primary,
	400: primitiveColors.chartBlue400,
	300: primitiveColors.chartBlue300,
	200: primitiveColors.chartBlue200,
	100: primitiveColors.chartBlue100,
	50:  primitiveColors.chartBlue50,
} as const;

export const colorTokens = {
	primitive: primitiveColors,
	brand: brandTokens,
	text: {
		primary:   primitiveColors.gray900,
		strong:    primitiveColors.gray850,
		secondary: primitiveColors.gray800,
		muted:     primitiveColors.gray700,   // ⚠ gray700 역전 주석 참조
		readonly:  primitiveColors.gray650,   // ⚠ gray650 역전 주석 참조
		subtle:    primitiveColors.gray600,
		helper:    primitiveColors.gray650,  // v0.2 정리: gray575(#888,3.54:1 미달) → gray650(#5E5E5E,6.4:1 AA)
		dim:       primitiveColors.gray595,   // ⚠ gray595 역전 주석 참조
		panel:     primitiveColors.gray590,   // ⚠ gray590 역전 주석 참조
		label:     primitiveColors.grayWarm,  // v0.2: gray580 → grayWarm
		detail:    primitiveColors.grayCool,  // v0.2: gray605 → grayCool
		body:      primitiveColors.gray750,
		tertiary:  primitiveColors.gray550,
		disabled:  primitiveColors.gray500,
		inverse:   primitiveColors.white,
		accent:    brandTokens.primary,
		danger:    primitiveColors.danger,
		success:   primitiveColors.success500,
		warning:   primitiveColors.warning500,
	},
	background: {
		canvas:      primitiveColors.white,
		surface:     primitiveColors.gray50,
		elevated:    primitiveColors.white,
		subtle:      primitiveColors.subtleBackground,
		selected:    primitiveColors.selectedBackground,
		inverse:     primitiveColors.gray900,
		strong:      primitiveColors.gray850,
		accent:      primitiveColors.blue50,
		accentSoft:  primitiveColors.accentSoftBackground,
		accentChip:  primitiveColors.accentChipBackground,
		tabAccent:   primitiveColors.researchTabBackground,
		tableAccent: primitiveColors.summaryTableAccent,
		accentMuted: primitiveColors.blue100,
		disabled:    primitiveColors.gray400,
		danger:      primitiveColors.dangerAction,
		dangerHover: primitiveColors.dangerActionHover,
		errorAccent: primitiveColors.errorAccent,
	},
	border: {
		// --- neutral: 진할수록 강조. default = 라이브 최다 사용 divider ---
		// v0.2 정리: default·light(#EDEDED 중복) / subtle(#E0E0E0) / strong(#D9D9D9)
		//   / neutral·muted(#CCCCCC 중복) / hint(#AAAAAA) 7개를 명도순 3단계로 수렴.
		default:      primitiveColors.gray200,  // #EDEDED  기본 divider
		strong:       primitiveColors.gray400,  // #D9D9D9  강조 보더(카드·인풋)
		strongest:    primitiveColors.gray525,  // #AAAAAA  최강조 보더
		// --- semantic (유지) ---
		accent:       brandTokens.primary,
		accentMuted:  primitiveColors.blue300,
		inverse:      primitiveColors.gray600,
		danger:       primitiveColors.danger,
		errorAccent:  primitiveColors.errorAccent,
	},
	icon: {
		default: primitiveColors.gray800,
		subtle:  primitiveColors.gray600,
		inverse: primitiveColors.white,
		accent:  brandTokens.primary,
		danger:  primitiveColors.danger,
		error:   primitiveColors.iconDanger,
		success: primitiveColors.success500,
	},
	action: {
		info:         primitiveColors.timelineAccent,
		selected:     primitiveColors.researchSelected,
		excel:        primitiveColors.excelGreen,
		danger:       primitiveColors.dangerAction,
		dangerOutline:primitiveColors.dangerOutline,
		dangerHover:  primitiveColors.dangerActionHover,
	},
	metric: {
		danger: primitiveColors.metricDanger,
		high:   primitiveColors.metricDanger,
		medium: primitiveColors.warning500,
		low:    primitiveColors.metricLowGreen,
	},
	chart: {
		blueScale: chartBlueScale,
		// 차트 색상은 진한색에서 연한색 순서로 렌더링합니다.
		blueScaleSequence: [
			chartBlueScale[900],
			chartBlueScale[800],
			chartBlueScale[500],
			chartBlueScale[400],
			chartBlueScale[300],
			chartBlueScale[200],
			chartBlueScale[100],
			chartBlueScale[50],
		],
		trendSequence: [
			primitiveColors.trendMint100,
			primitiveColors.trendCyan200,
			primitiveColors.trendSky300,
			primitiveColors.trendBlue400,
			primitiveColors.trendBlue500,
			primitiveColors.trendIndigo600,
			primitiveColors.trendNavy700,
		],
	},
	topic: {
		objective: {
			background: "#FFF5DB",
			text:       "#66531D",
			border:     "#66531D",
		},
		solution: {
			background: "#CDF3E2",
			text:       "#024E2D",
			border:     "#024E2D",
		},
	},
	overlay: {
		loading:  "rgba(0, 0, 0, 0.20)",
		tutorial: "rgba(0, 0, 0, 0.40)",
		disabled: "rgba(255, 255, 255, 0.50)",
	},
	status: {
		online:            primitiveColors.success300,
		successBackground: "#F0FDF4",
		dangerBackground:  "#FFF1F0",
	},
	info: {
		background: primitiveColors.blue100,
		text:       primitiveColors.infoText,
	},
	highlight: {
		keywordBackground: primitiveColors.warning100,
	},
	event: {
		bannerGradientStart: primitiveColors.eventBannerStart,
		bannerGradientEnd:   primitiveColors.eventBannerEnd,
		buttonHover:         primitiveColors.eventButtonHover,
	},
	landing: {
		cloud: {
			primary:         "#1A3C6E",
			accent:          "#2D7DD2",
			accentSecondary: "#5B6EEB",
			surface:         "#F4F7FB",
			panel:           "#F8FAFC",
			badge:           "#EFF6FF",
			ink:             "#0F0F1A",
			highlight:       "#D97706",
		},
		intro: {
			heroGradientStart:        "#B2C8FF",
			heroAccent:               "#5484FF",
			aboutSelectedBackground:  "#EBF0F9",
			sectionDark:              "#0A1D5B",
			sectionDarker:            "#0B0865",
			cardDark:                 "#08064D",
			cardAccent:               "#3F5394",
			sectionTint:              "#ECF2FF",
			tryBackground:            "#91C3FF",
			hookBackground:           "#FFF2E0",
			hookAccent:               "#FF8637",
			caseWarm:                 "#F7E6D7",
			caseCool:                 "#E3F2F8",
			caseSoft:                 "#D8DDFC",
			contactBackground:        "#003362",
			featureBullet:            "#285EFB",
		},
	},
} as const;

export const typographyTokens = {
	fontFamily: {
		sans: "Pretendard",
	},
	fontWeight: {
		regular:   400,
		medium:    500,
		semibold:  600,
		bold:      700,
		extrabold: 800,
	},
	// v0.2 신설: 타입 스케일 (SaaS 컴팩트, 7스텝)
	fontSize: {
		xs:   "12px",
		sm:   "14px",
		base: "16px",
		lg:   "18px",
		xl:   "20px",
		"2xl":"24px",
		"3xl":"30px",
	},
	lineHeight: {
		tight:  1.3, // 제목
		snug:   1.4, // 레이블/캡션
		normal: 1.5, // 본문
	},
} as const;

/**
 * 역할 기반 텍스트 스타일 (size + weight + lineHeight 묶음).
 * 사용자 앵커: 섹션제목 18/semibold · item제목 16/semibold · 본문 16/regular
 *            · 버튼 14/semibold · 레이블 12/medium. 나머지는 표준 램프로 보강.
 */
export const textStyles = {
	display:   { fontSize: "30px", fontWeight: 700, lineHeight: 1.3 },
	h1:        { fontSize: "24px", fontWeight: 700, lineHeight: 1.3 },
	h2:        { fontSize: "18px", fontWeight: 600, lineHeight: 1.4 }, // 섹션 제목
	itemTitle: { fontSize: "16px", fontWeight: 600, lineHeight: 1.5 },
	body:      { fontSize: "16px", fontWeight: 400, lineHeight: 1.5 },
	bodySm:    { fontSize: "14px", fontWeight: 400, lineHeight: 1.5 },
	button:    { fontSize: "14px", fontWeight: 600, lineHeight: 1.0 },
	label:     { fontSize: "12px", fontWeight: 500, lineHeight: 1.4 },
	caption:   { fontSize: "12px", fontWeight: 400, lineHeight: 1.4 },
} as const;

export const spacingTokens = {
	0:  "0px",
	1:  "4px",
	2:  "8px",
	3:  "12px",
	4:  "16px",
	5:  "20px",
	6:  "24px",
	8:  "32px",
	10: "40px",
	12: "48px",
} as const;

export const radiusTokens = {
	xs:    "4px",
	sm:    "8px",
	md:    "10px",
	lg:    "12px",
	xl:    "16px",
	round: "999px",
} as const;

export const shadowTokens = {
	button:      "0 2px 4px rgba(0, 0, 0, 0.2)",
	header:      "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
	floating:    "0px 8px 24px -6px rgba(0, 0, 0, 0.10)",
	popover:     "0px 8px 24px -6px rgba(0, 0, 0, 0.12)",
	tooltip:     "0 4px 20px rgba(0, 0, 0, 0.15)",
	bannerText:  "0px 4px 4px rgba(0, 0, 0, 0.25)",
	alertIcon:   "0px 0px 64px rgba(245, 72, 72, 0.35), 0px 1px 2px rgba(0, 0, 0, 0.08)",
	snackbar:    "0px 8px 24px -6px rgba(0, 0, 0, 0.30)",
	stickyHeader:"0px 1px 1px -1px rgba(0, 0, 0, 0.10)",
	ctaModal:    "0px 8px 65px 0px rgba(40, 76, 149, 0.20)",
} as const;

export const themeModeTokens = {
	light: {
		palette: {
			mode: "light",
			primary: {
				main: colorTokens.brand.primary,
				dark: colorTokens.primitive.gray400,
			},
			info: {
				main: colorTokens.primitive.white,
			},
			background: {
				default: colorTokens.primitive.neutral700,
				paper:   colorTokens.primitive.white,
			},
			text: {
				primary:   colorTokens.text.primary,
				secondary: colorTokens.text.secondary,
			},
		},
	},
	dark: {
		palette: {
			mode: "dark",
			primary: {
				main: colorTokens.primitive.neutral700,
				dark: colorTokens.primitive.black,
			},
			background: {
				default: colorTokens.primitive.neutral950,
				paper:   colorTokens.primitive.neutral900,
			},
			text: {
				primary:   colorTokens.text.inverse,
				secondary: colorTokens.primitive.gray400,
			},
		},
	},
} as const;

export const designTokens = {
	color:      colorTokens,
	typography: typographyTokens,
	textStyles: textStyles,
	spacing:    spacingTokens,
	radius:     radiusTokens,
	shadow:     shadowTokens,
	theme:      themeModeTokens,
} as const;

export type DesignTokens = typeof designTokens;

export default designTokens;

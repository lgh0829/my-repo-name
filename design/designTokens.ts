/**
 * @file 디자인 토큰 정의
 * @description MUI 테마와 Tailwind 설정에서 함께 참조할 스타일 기준값을 관리합니다.
 * @author yunjulee
 * @lastModified 2026-04-07
 */

const primitiveColors = {
	white: "#FFFFFF",
	black: "#000000",
	blue50: "#F3F6FC",
	blue100: "#EBF0FA",
	blue300: "#A3BCE8",
	blue500: "#3361BE",
	chartBlue50: "#EBF0FA",
	chartBlue100: "#CBD7F1",
	chartBlue200: "#A3B9E6",
	chartBlue300: "#7A9ADB",
	chartBlue400: "#527CD1",
	chartBlue800: "#284C95",
	chartBlue900: "#1D376D",
	infoText: "#014361",
	gray50: "#FAFAFA",
	gray100: "#F5F5F5",
	gray200: "#EDEDED",
	gray250: "#EEEEEE",
	gray300: "#E0E0E0",
	gray400: "#D9D9D9",
	gray425: "#CCCCCC",
	gray450: "#DDDDDD",
	gray500: "#BDBDBD",
	gray525: "#AAAAAA",
	gray550: "#9E9E9E",
	gray575: "#888888",
	gray580: "#72777A",
	gray590: "#666666",
	gray595: "#777777",
	gray600: "#757575",
	gray605: "#595D62",
	gray650: "#5E5E5E",
	gray700: "#616161",
	gray750: "#494949",
	gray800: "#424242",
	gray850: "#212121",
	gray900: "#1E1E1E",
	neutral700: "#333333",
	neutral900: "#171717",
	neutral950: "#111111",
	// Red 계열은 색상 scale이 아니라 현재 UI 사용 맥락 기준으로 분리합니다.
	danger: "#FF3232",
	dangerAction: "#F54848",
	dangerActionHover: "#E55648",
	errorAccent: "#FD6051",
	metricDanger: "#FB2828",
	iconDanger: "#EF4444",
	success300: "#7DDE86",
	success500: "#22C55E",
	warning500: "#FFAB03",
	warning100: "#FFE4B5",
	eventBannerStart: "#6FC6F1",
	eventBannerEnd: "#483EBF",
	eventButtonHover: "#F5FAFF",
	selectedBackground: "#EBEFF8",
	subtleBackground: "#F4F4F4",
	accentSoftBackground: "#E8F0FE",
	accentChipBackground: "#EEF2FF",
	researchTabBackground: "#EDF2FF",
	summaryTableAccent: "#D7E1F5",
	timelineAccent: "#1976D2",
	researchSelected: "#2F55A3",
	dangerOutline: "#EF3535",
	trendMint100: "#C6E3CB",
	trendCyan200: "#83CACF",
	trendSky300: "#47AED0",
	trendBlue400: "#3984B6",
	trendBlue500: "#2C5A9C",
	trendIndigo600: "#1E3082",
	trendNavy700: "#141C59",
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
	50: primitiveColors.chartBlue50,
} as const;

export const colorTokens = {
	primitive: primitiveColors,
	brand: brandTokens,
	text: {
		primary: primitiveColors.gray900,
		strong: primitiveColors.gray850,
		secondary: primitiveColors.gray800,
		muted: primitiveColors.gray700,
		readonly: primitiveColors.gray650,
		subtle: primitiveColors.gray600,
		helper: primitiveColors.gray575,
		dim: primitiveColors.gray595,
		panel: primitiveColors.gray590,
		label: primitiveColors.gray580,
		detail: primitiveColors.gray605,
		body: primitiveColors.gray750,
		tertiary: primitiveColors.gray550,
		disabled: primitiveColors.gray500,
		inverse: primitiveColors.white,
		accent: brandTokens.primary,
		danger: primitiveColors.danger,
		success: primitiveColors.success500,
		warning: primitiveColors.warning500,
	},
	background: {
		canvas: primitiveColors.white,
		surface: primitiveColors.gray50,
		elevated: primitiveColors.white,
		subtle: primitiveColors.subtleBackground,
		selected: primitiveColors.selectedBackground,
		inverse: primitiveColors.gray900,
		strong: primitiveColors.gray850,
		accent: primitiveColors.blue50,
		accentSoft: primitiveColors.accentSoftBackground,
		accentChip: primitiveColors.accentChipBackground,
		tabAccent: primitiveColors.researchTabBackground,
		tableAccent: primitiveColors.summaryTableAccent,
		accentMuted: primitiveColors.blue100,
		disabled: primitiveColors.gray400,
		danger: primitiveColors.dangerAction,
		dangerHover: primitiveColors.dangerActionHover,
		errorAccent: primitiveColors.errorAccent,
	},
	border: {
		default: primitiveColors.gray200,
		light: primitiveColors.gray250,
		subtle: primitiveColors.gray300,
		strong: primitiveColors.gray400,
		neutral: primitiveColors.gray425,
		hint: primitiveColors.gray525,
		muted: "#CDCDCD",
		accent: brandTokens.primary,
		accentMuted: primitiveColors.blue300,
		inverse: primitiveColors.gray600,
		danger: primitiveColors.danger,
		errorAccent: primitiveColors.errorAccent,
	},
	icon: {
		default: primitiveColors.gray800,
		subtle: primitiveColors.gray600,
		inverse: primitiveColors.white,
		accent: brandTokens.primary,
		danger: primitiveColors.danger,
		error: primitiveColors.iconDanger,
		success: primitiveColors.success500,
	},
	action: {
		info: primitiveColors.timelineAccent,
		selected: primitiveColors.researchSelected,
		excel: "#6EB92C",
		danger: primitiveColors.dangerAction,
		dangerOutline: primitiveColors.dangerOutline,
		dangerHover: primitiveColors.dangerActionHover,
	},
	metric: {
		danger: primitiveColors.metricDanger,
		high: primitiveColors.metricDanger,
		medium: primitiveColors.warning500,
		low: "#22CC00",
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
			text: "#66531D",
			border: "#66531D",
		},
		solution: {
			background: "#CDF3E2",
			text: "#024E2D",
			border: "#024E2D",
		},
	},
	overlay: {
		loading: "rgba(0, 0, 0, 0.20)",
		tutorial: "rgba(0, 0, 0, 0.40)",
		disabled: "rgba(255, 255, 255, 0.50)",
	},
	status: {
		online: primitiveColors.success300,
		successBackground: "#F0FDF4",
		dangerBackground: "#FFF1F0",
	},
	info: {
		background: primitiveColors.blue100,
		text: primitiveColors.infoText,
	},
	highlight: {
		keywordBackground: primitiveColors.warning100,
	},
	event: {
		bannerGradientStart: primitiveColors.eventBannerStart,
		bannerGradientEnd: primitiveColors.eventBannerEnd,
		buttonHover: primitiveColors.eventButtonHover,
	},
	landing: {
		cloud: {
			primary: "#1A3C6E",
			accent: "#2D7DD2",
			accentSecondary: "#5B6EEB",
			surface: "#F4F7FB",
			panel: "#F8FAFC",
			badge: "#EFF6FF",
			ink: "#0F0F1A",
			highlight: "#D97706",
		},
		intro: {
			heroGradientStart: "#B2C8FF",
			heroAccent: "#5484FF",
			aboutSelectedBackground: "#EBF0F9",
			sectionDark: "#0A1D5B",
			sectionDarker: "#0B0865",
			cardDark: "#08064D",
			cardAccent: "#3F5394",
			sectionTint: "#ECF2FF",
			tryBackground: "#91C3FF",
			hookBackground: "#FFF2E0",
			hookAccent: "#FF8637",
			caseWarm: "#F7E6D7",
			caseCool: "#E3F2F8",
			caseSoft: "#D8DDFC",
			contactBackground: "#003362",
			featureBullet: "#285EFB",
		},
	},
} as const;

export const typographyTokens = {
	fontFamily: {
		sans: "Pretendard",
	},
	fontWeight: {
		regular: 400,
		medium: 500,
		semibold: 600,
		bold: 700,
		extrabold: 800,
	},
} as const;

export const spacingTokens = {
	0: "0px",
	1: "4px",
	2: "8px",
	3: "12px",
	4: "16px",
	5: "20px",
	6: "24px",
	8: "32px",
	10: "40px",
	12: "48px",
} as const;

export const radiusTokens = {
	xs: "4px",
	sm: "8px",
	md: "10px",
	lg: "12px",
	xl: "16px",
	round: "999px",
} as const;

export const shadowTokens = {
	button: "0 2px 4px rgba(0, 0, 0, 0.2)",
	header: "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
	floating: "0px 8px 24px -6px rgba(0, 0, 0, 0.10)",
	popover: "0px 8px 24px -6px rgba(0, 0, 0, 0.12)",
	tooltip: "0 4px 20px rgba(0, 0, 0, 0.15)",
	bannerText: "0px 4px 4px rgba(0, 0, 0, 0.25)",
	alertIcon:
		"0px 0px 64px rgba(245, 72, 72, 0.35), 0px 1px 2px rgba(0, 0, 0, 0.08)",
	snackbar: "0px 8px 24px -6px rgba(0, 0, 0, 0.30)",
	stickyHeader: "0px 1px 1px -1px rgba(0, 0, 0, 0.10)",
	ctaModal: "0px 8px 65px 0px rgba(40, 76, 149, 0.20)",
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
				paper: colorTokens.primitive.white,
			},
			text: {
				primary: colorTokens.text.primary,
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
				paper: colorTokens.primitive.neutral900,
			},
			text: {
				primary: colorTokens.text.inverse,
				secondary: colorTokens.primitive.gray400,
			},
		},
	},
} as const;

export const designTokens = {
	color: colorTokens,
	typography: typographyTokens,
	spacing: spacingTokens,
	radius: radiusTokens,
	shadow: shadowTokens,
	theme: themeModeTokens,
} as const;

export type DesignTokens = typeof designTokens;

export default designTokens;

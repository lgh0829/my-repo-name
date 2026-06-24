/**
 * @file 디자인 토큰 정의
 * @description MUI 테마와 Tailwind 설정에서 함께 참조할 스타일 기준값을 관리합니다.
 * @author yunjulee
 * @version 0.4.4
 * @lastModified 2026-06-24
 *
 * --- v0.2 변경 내역 ---
 * [제거] gray100, gray450 — 미참조
 * [이름변경] gray580→grayWarm, gray605→grayCool (text.label/detail 전용)
 * [문서화] 명도 역전 구간 주석 추가
 *
 * --- v0.3 변경 내역 ---
 * [Gray ramp 재정비] ~22스텝 → 12스텝 균등 램프
 *   · 역전 구간 완전 제거 (gray590/595, gray650/700)
 * [Text semantic 통합] 고유 색상값 ~14개 → 6개 (토큰 이름 유지, product 호환)
 * [grayWarm/grayCool 폐기] → gray700/gray800으로 수렴 (ΔE<2)
 * [subtleBackground 폐기] → gray100으로 통합
 *
 * --- v0.4 변경 내역 ---
 * [Gray 번호 재정비] ΔE2000 인접 스텝 기반으로 50/100/150 단위 재부여
 *   · ΔE < 9  → 50 간격, ΔE 9~12 → 100 간격, ΔE > 12 → 150 간격
 *   · 최어둠 gray950 → gray900 확정
 *   · 매핑: 구 gray200→gray150, gray300→gray200, gray400→gray250,
 *           gray500→gray400, gray600→gray450, gray700→gray600,
 *           gray750→gray650, gray800→gray700, gray900→gray800, gray950→gray900
 *   · 숫자 공백(250→400, 450→600)은 팔레트의 실제 지각 단절을 반영
 *
 * --- v0.4.1 변경 내역 ---
 * [grayDisabled → gray300] #BDBDBD를 ramp에 편입 (gray250 바로 다음 슬롯)
 *   · v0.4 번호 체계(gray400/450/600/…) 유지 — 연쇄 rename 없음
 *   · grayDisabled 제거. text.disabled / background.disabled → gray300
 *
 * --- v0.4.3 변경 내역 ---
 * [Special primitives → blue scale 편입]
 *   · ΔE < 2 그룹(selectedBg/accentSoftBg/accentChipBg/researchTabBg) → blue100 흡수
 *   · summaryTableAccent → blue200 / timelineAccent → blue400 / researchSelected → blue600
 *   · primitiveColors에서 의미명 7개 제거, blue scale 3슬롯 신설
 *
 * --- v0.4.2 변경 내역 ---
 * [Red/Danger 스케일화] 의미명(danger, dangerAction…) → ΔE2000 기반 50단위 스케일
 *   · L=62~69% 범위, 전 구간 ΔE 2.9~5.2 → 50단위 균등
 *   · danger400(#FD6051, 밝음) → danger700(#EF3535, 어둠)
 *   · danger500(#FF3232) = 기준 main red
 *   · 매핑: errorAccent→400, dangerAction→450, danger→500,
 *           dangerActionHover→550, iconDanger→600, metricDanger→650, dangerOutline→700
 *
 * --- v0.4.4 변경 내역 ---
 * [border 시맨틱 재정비] 실사용 기준 이름·값 재배정 (PatSol-Front audit 결과 반영)
 *   · 구 3단계(default/strong/strongest) → 4단계(subtle/default/muted/neutral)
 *   · 이름 재배정: default(gray150)→subtle / strong(gray250)→muted / strongest(gray400)→neutral
 *   · default는 gray200(#E0E0E0)으로 재배정 — "기본 카드·인풋 보더"에 더 적합한 값
 *   · 제거: strong(→muted로 이관) / strongest(0회 미사용, →neutral로 이관)
 *   · PatSol-Front 실사용 빈도: subtle 70회+, muted 30회+, neutral 10회+, default 10회
 */

const primitiveColors = {
	white: "#FFFFFF",
	black: "#000000",

	// --- Blue ---
	blue50: "#F3F6FC",  // background.accent (연한 파랑 배경)
	blue100: "#EBF0FA",  // background.accentMuted / selected / accentSoft / accentChip / tabAccent
	blue200: "#D7E1F5",  // background.tableAccent (was summaryTableAccent, ΔE 5.2 from blue100)
	blue300: "#A3BCE8",  // border.accentMuted
	blue400: "#1976D2",  // action.info (was timelineAccent, MUI blue, L=56%)
	blue500: "#3361BE",  // brand.primary
	blue600: "#2F55A3",  // action.selected (was researchSelected, L=46%)

	// --- Chart Blue ---
	chartBlue50: "#EBF0FA",
	chartBlue100: "#CBD7F1",
	chartBlue200: "#A3B9E6",
	chartBlue300: "#7A9ADB",
	chartBlue400: "#527CD1",
	chartBlue800: "#284C95",
	chartBlue900: "#1D376D",

	// --- Info ---
	infoText: "#014361",

	// --- Gray Scale (13 steps, ΔE-proportional numbering) ---
	// v0.4.1: v0.4 번호 체계 유지 + gray300(#BDBDBD) 추가.
	// gray300→gray400 간격(100)은 ΔE 5.2 기준보다 넓으나, 연쇄 rename 대신 단순 편입.
	// 숫자 공백(250→400, 450→600)은 팔레트의 실제 지각 단절을 반영한다.
	gray50: "#FAFAFA",  // background.surface
	gray100: "#F5F5F5",  // background.subtle      +50  ΔE  1.0
	gray150: "#EDEDED",  // border.subtle           +50  ΔE  1.7
	gray200: "#E0E0E0",  // border.default          +50  ΔE  2.8
	gray250: "#D9D9D9",  // border.muted            +50  ΔE  1.6
	gray300: "#BDBDBD",  // text/bg.disabled        +50  ΔE  6.9
	gray400: "#AAAAAA",  // border.strongest        +100 ΔE  5.2
	gray450: "#9E9E9E",  // text.tertiary           +50  ΔE  3.6
	gray600: "#757575",  // text.subtle             +150 ΔE 14.5 ← 단절
	gray650: "#666666",  // text.panel              +50  ΔE  5.8
	gray700: "#5E5E5E",  // text.muted		         +50  ΔE  3.0
	gray800: "#424242",  // text.secondary          +100 ΔE  9.7
	gray900: "#1E1E1E",  // text.primary            +100 ΔE 11.5

	// --- Neutral (dark mode / strong backgrounds) ---
	neutral700: "#333333",
	neutral900: "#171717",
	neutral950: "#111111",

	// --- Red / Danger (7 steps, ΔE-proportional numbering) ---
	// v0.4.2: ΔE2000 기반 50단위 스케일. danger400(밝음) → danger700(어둠).
	// 전 구간 ΔE 2.9~5.2, L=62~69% 범위. danger500 = 기준 main red.
	danger400: "#FD6051",  // bg.errorAccent (coral)              L=69.1%
	danger450: "#F54848",  // action.danger / bg.danger           +50  ΔE  5.1
	danger500: "#FF3232",  // text.danger / border.danger (기준)   +50  ΔE  3.9
	danger550: "#E55648",  // action.dangerHover / bg.dangerHover +50  ΔE  5.2
	danger600: "#EF4444",  // icon.error                         +50  ΔE  3.3
	danger650: "#FB2828",  // metric.danger / metric.high         +50  ΔE  4.9
	danger700: "#EF3535",  // action.dangerOutline (어둠)          +50  ΔE  2.9

	// --- Success / Warning ---
	success300: "#7DDE86",
	success500: "#22C55E",
	warning500: "#FFAB03",
	warning100: "#FFE4B5",

	// --- Action / Metric greens (semantic 직박힘 정리: primitive 경유) ---
	excelGreen: "#6EB92C", // action.excel 전용 (Excel 내보내기 버튼)
	metricLowGreen: "#22CC00", // metric.low 전용 (낮음 지표)

	// --- Event / Marketing ---
	eventBannerStart: "#6FC6F1",
	eventBannerEnd: "#483EBF",
	eventButtonHover: "#F5FAFF",

	// --- Chart: Trend ---
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
	// v0.3 정리: 고유 색상값 ~14개 → 6개로 통합. 토큰 이름은 product 호환성 유지.
	// 잔여 2단계 (gray650·grayDisabled) 추가 수렴은 디자이너 합의 후 Phase 2에서 진행.
	text: {
		// Tier 1 — #1E1E1E
		// 의견: strong, body, readonly 시멘틱을 primary로 흡수하는 방안 제안.
		primary: primitiveColors.gray900,
		strong: primitiveColors.gray900,   // 구 gray850 #212121 → ΔE0.3 통합
		body: primitiveColors.gray900,   // 구 gray750 #494949 → ΔE1.4 통합
		readonly: primitiveColors.gray900,	  // 구 gray650 #5E5E5E → 가독성 위해 gray900으로 통합
		// Tier 2 — #424242
		secondary: primitiveColors.gray800,
		// Tier 3a — #5E5E5E
		// 의견: alias 각각의 명칭은 유지하되, 동일 색상으로 구현.
		muted: primitiveColors.gray700,   // 구 gray700 #616161 → ΔE0.8 통합
		helper: primitiveColors.gray700,
		detail: primitiveColors.gray700,   // 구 grayCool #595D62 → ΔE1.2 통합
		panel: primitiveColors.gray700,   // 구 gray590 #666666 → ΔE3.0 (1x only, 수렴)
		// Tier 3b — #757575
		subtle: primitiveColors.gray600,
		dim: primitiveColors.gray600,   // 구 gray595 #777777 → ΔE0.7 통합
		label: primitiveColors.gray600,   // 구 grayWarm #72777A → ΔE1.5 통합
		// Tier 4 — #9E9E9E
		tertiary: primitiveColors.gray450,
		// Tier 5 — #BDBDBD (gray300으로 ramp 편입)
		disabled: primitiveColors.gray300,
		// Fixed
		inverse: primitiveColors.white,
		accent: brandTokens.primary,
		danger: primitiveColors.danger500,
		success: primitiveColors.success500,
		warning: primitiveColors.warning500,
	},
	background: {
		// Group 1: Neutral
		// 제안: inverse, strong 시멘틱을 inverse로 합치는 방향 제안. (기존 gray800 -> gray900)
		canvas: primitiveColors.white,
		surface: primitiveColors.gray50,
		elevated: primitiveColors.white,
		subtle: primitiveColors.gray100,
		selected: primitiveColors.blue100,    // was selectedBackground (#EBEFF8, ΔE 0.6)
		inverse: primitiveColors.gray800,
		strong: primitiveColors.gray900,
		// Group 2: Brand
		// 제안: accentMuted, accentSoft, accentChip, tabAccent 시멘틱을 모두 accentMuted로 합치는 방향 제안.
		accent: primitiveColors.blue50,
		accentSoft: primitiveColors.blue100,  // was accentSoftBackground (#E8F0FE, ΔE 1.8)
		accentChip: primitiveColors.blue100,  // was accentChipBackground (#EEF2FF, ΔE 1.7)
		tabAccent: primitiveColors.blue100,   // was researchTabBackground (#EDF2FF, ΔE 1.4)
		tableAccent: primitiveColors.blue200, // was summaryTableAccent
		accentMuted: primitiveColors.blue100,
		// Group 3: Status
		disabled: primitiveColors.gray300,
		danger: primitiveColors.danger450,
		dangerHover: primitiveColors.danger550,
		errorAccent: primitiveColors.danger400,
	},
	border: {
		// Group 1: Neutral — gray 기반 구분선. subtle(연함) → neutral(진함) 순.
		// v0.4.4: 구 default/strong/strongest → subtle/default/muted/neutral 4단계 재정비.
		subtle: primitiveColors.gray150,  // #EDEDED  가장 연한 hr·divider
		default: primitiveColors.gray200,  // #E0E0E0  카드·모달·인풋 표준 보더
		muted: primitiveColors.gray250,  // #D9D9D9  테이블 셀·파일업로드·강조 섹션 보더
		neutral: primitiveColors.gray400,  // #AAAAAA  가장 진한 중립 보더 (Research 탭·아이템)
		inverse: primitiveColors.gray600,  // #757575  어두운 배경 위 보더
		// Group 2: Brand — 파랑 기반 보더
		accent: brandTokens.primary,      // #3361BE  focus ring, 선택 상태 보더
		accentMuted: primitiveColors.blue300,  // #A3BCE8  연한 파랑 보더
		// Group 3: Status — 상태 표현 보더
		danger: primitiveColors.danger500,  // #FF3232  오류 폼 보더
		errorAccent: primitiveColors.danger400,  // #FD6051  오류 장식 보더 (dashed 포함)
	},
	icon: {
		// Group 1: Neutral — gray 기반 아이콘 색
		default: primitiveColors.gray800,  // #424242  기본 아이콘
		subtle:  primitiveColors.gray600,  // #757575  부가·보조 아이콘
		inverse: primitiveColors.white,    // #FFFFFF  어두운 배경 위 아이콘
		// Group 2: Brand — 파랑 기반 아이콘
		accent:  brandTokens.primary,      // #3361BE  브랜드 강조 아이콘
		// Group 3: Status — 상태 표현 아이콘
		danger:  primitiveColors.danger500,  // #FF3232  오류·위험 아이콘
		error:   primitiveColors.danger600,  // #EF4444  에러 아이콘 (icon.error 전용)
		success: primitiveColors.success500, // #22C55E  성공 아이콘
	},
	action: {
		// Group 1: Brand — 파랑 기반 인터랙션
		info:     primitiveColors.blue400,   // #1976D2  타임라인·정보 액션
		selected: primitiveColors.blue600,   // #2F55A3  선택 상태 액션
		// Group 2: Utility — 특정 도구 전용
		excel:    primitiveColors.excelGreen, // #6EB92C  Excel 내보내기 버튼 전용
		// Group 3: Status — danger 계열 액션
		danger:       primitiveColors.danger450,  // #F54848  Danger 버튼 fill
		dangerHover:  primitiveColors.danger550,  // #E55648  Danger 버튼 hover
		dangerOutline: primitiveColors.danger700, // #EF3535  Danger outline 버튼
	},
	metric: {
		// 의견: high 시멘틱을 danger로 흡수하는 방안 제안.
		danger: primitiveColors.danger650,
		high: primitiveColors.danger650,
		medium: primitiveColors.warning500,
		low: primitiveColors.metricLowGreen,
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
	// v0.2 신설: 타입 스케일 (SaaS 컴팩트, 7스텝)
	fontSize: {
		xs: "12px",
		sm: "14px",
		base: "16px",
		lg: "18px",
		xl: "20px",
		"2xl": "24px",
		"3xl": "30px",
	},
	lineHeight: {
		tight: 1.3, // 제목
		snug: 1.4, // 레이블/캡션
		normal: 1.5, // 본문
	},
} as const;

/**
 * 역할 기반 텍스트 스타일 (size + weight + lineHeight 묶음).
 * 사용자 앵커: 섹션제목 18/semibold · item제목 16/semibold · 본문 16/regular
 *            · 버튼 14/semibold · 레이블 12/medium. 나머지는 표준 램프로 보강.
 */
export const textStyles = {
	display: { fontSize: "30px", fontWeight: 700, lineHeight: 1.3 },
	h1: { fontSize: "24px", fontWeight: 700, lineHeight: 1.3 },
	h2: { fontSize: "18px", fontWeight: 600, lineHeight: 1.4 }, // 섹션 제목
	itemTitle: { fontSize: "16px", fontWeight: 600, lineHeight: 1.5 },
	body: { fontSize: "16px", fontWeight: 400, lineHeight: 1.5 },
	bodySm: { fontSize: "14px", fontWeight: 400, lineHeight: 1.5 },
	button: { fontSize: "14px", fontWeight: 600, lineHeight: 1.0 },
	label: { fontSize: "12px", fontWeight: 500, lineHeight: 1.4 },
	caption: { fontSize: "12px", fontWeight: 400, lineHeight: 1.4 },
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
	alertIcon: "0px 0px 64px rgba(245, 72, 72, 0.35), 0px 1px 2px rgba(0, 0, 0, 0.08)",
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
				dark: colorTokens.primitive.gray250,
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
	textStyles: textStyles,
	spacing: spacingTokens,
	radius: radiusTokens,
	shadow: shadowTokens,
	theme: themeModeTokens,
} as const;

export type DesignTokens = typeof designTokens;

export default designTokens;

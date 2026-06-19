/**
 * 컴포넌트 → 기대 토큰 매핑 + 실측 셀렉터/노드 정의.
 * 라이브(patsol.kr)·Figma 실측의 대상 목록. (docs/harness/component_measurement.md)
 */
export interface ComponentSpec {
	component: string;
	/** patsol.kr DOM 셀렉터 (라이브 실측용) */
	selector?: string;
	/** Figma node id (Figma 실측용) */
	nodeId?: string;
	/** 기대 토큰 경로 */
	expects: { color?: string; background?: string; border?: string };
	props: Array<"color" | "backgroundColor" | "borderColor" | "boxShadow" | "borderRadius">;
}

export const componentSpecs: ComponentSpec[] = [
	// --- patsol.kr/home 에서 실측되는 마케팅 컴포넌트 ---
	{
		component: "featureCard",
		selector: "a[class*=MuiButton]",
		expects: { background: "color.background.elevated", color: "color.text.primary" },
		props: ["backgroundColor", "color", "borderRadius", "boxShadow"],
	},
	{
		component: "ctaSearchButton",
		selector: "a[href*=search]",
		expects: { color: "color.text.subtle" },
		props: ["color", "borderRadius", "boxShadow"],
	},
	{
		component: "bodyText",
		selector: "p",
		expects: { color: "color.text.primary" },
		props: ["color"],
	},
	// --- 로그인 후 앱 내부에서 측정 (현재 미측정) ---
	{
		component: "primaryButton",
		selector: "button[class*='primary'], .btn-primary",
		expects: { background: "color.brand.primary", color: "color.text.inverse" },
		props: ["backgroundColor", "color", "borderRadius", "boxShadow"],
	},
	{
		component: "dangerButton",
		selector: "button[class*='danger'], .btn-danger",
		expects: { background: "color.background.danger", color: "color.text.inverse" },
		props: ["backgroundColor", "color", "borderRadius"],
	},
	{
		component: "accentChip",
		selector: "[class*='chip'], [class*='tag']",
		expects: { background: "color.background.accentChip", color: "color.text.accent" },
		props: ["backgroundColor", "color", "borderRadius"],
	},
	{
		component: "card",
		selector: "[class*='card']",
		expects: { background: "color.background.elevated", border: "color.border.default" },
		props: ["backgroundColor", "borderColor", "borderRadius", "boxShadow"],
	},
	{
		component: "topicBadgeObjective",
		selector: "[class*='objective']",
		expects: { background: "color.topic.objective.background", color: "color.topic.objective.text" },
		props: ["backgroundColor", "color"],
	},
];

export default componentSpecs;

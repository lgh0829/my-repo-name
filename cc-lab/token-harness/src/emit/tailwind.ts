import { loadTokens } from "../load.ts";

const BANNER = `/**
 * ⚠ 생성된 파일 · 직접 수정 금지
 * SSOT: design/designTokens-v0.2.ts → token-harness 'tokens build'
 * 토큰을 바꾸려면 SSOT를 수정하고 다시 생성하세요.
 */`;

/** 배열(차트 시퀀스)은 인덱스 키 객체로 변환. */
function colorsBlock(color: Record<string, unknown>): unknown {
	const walk = (node: unknown): unknown => {
		if (Array.isArray(node)) {
			const obj: Record<string, unknown> = {};
			node.forEach((v, i) => (obj[String(i)] = walk(v)));
			return obj;
		}
		if (node && typeof node === "object") {
			const obj: Record<string, unknown> = {};
			for (const [k, v] of Object.entries(node)) obj[k] = walk(v);
			return obj;
		}
		return node;
	};
	return walk(color);
}

export function emitTailwind(): string {
	const t = loadTokens();
	const theme = {
		extend: {
			colors: colorsBlock(t.color as unknown as Record<string, unknown>),
			spacing: t.spacing,
			borderRadius: t.radius,
			boxShadow: t.shadow,
			fontFamily: { sans: [t.typography.fontFamily.sans, "sans-serif"] },
			fontWeight: t.typography.fontWeight,
			fontSize: t.typography.fontSize,
			lineHeight: t.typography.lineHeight,
		},
	};
	return `${BANNER}\nexport const patsolTheme = ${JSON.stringify(theme, null, 2)} as const;\n\nexport default patsolTheme;\n`;
}

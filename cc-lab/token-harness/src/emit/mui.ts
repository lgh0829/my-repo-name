import { loadTokens } from "../load.ts";

const BANNER = `/**
 * ⚠ 생성된 파일 · 직접 수정 금지
 * SSOT: design/designTokens-v0.2.ts → token-harness 'tokens build'
 */`;

/** radiusTokens.md ("10px") → 숫자 10. */
function radiusPx(v: string): number {
	const n = Number.parseFloat(v);
	return Number.isFinite(n) ? n : 8;
}

/** textStyles 역할 → MUI variant 매핑. */
const MUI_VARIANT: Record<string, string> = {
	display: "h1", h1: "h2", h2: "h3", itemTitle: "subtitle1",
	body: "body1", bodySm: "body2", button: "button", label: "overline", caption: "caption",
};

export function emitMui(): string {
	const t = loadTokens();
	const light = t.theme.light.palette;
	const dark = t.theme.dark.palette;
	const fontFamily = `"${t.typography.fontFamily.sans}", sans-serif`;
	const borderRadius = radiusPx(t.radius.md);

	const variants: Record<string, unknown> = { fontFamily };
	for (const [role, style] of Object.entries(t.textStyles)) {
		const v = MUI_VARIANT[role] ?? role;
		variants[v] = style;
	}

	return `${BANNER}
import { createTheme } from "@mui/material/styles";

const shared = {
  typography: ${JSON.stringify(variants, null, 2)},
  shape: { borderRadius: ${borderRadius} },
} as const;

export const lightTheme = createTheme({
  ...shared,
  palette: ${JSON.stringify(light, null, 2)},
});

export const darkTheme = createTheme({
  ...shared,
  palette: ${JSON.stringify(dark, null, 2)},
});

export default lightTheme;
`;
}

import { normalize } from "../normalize.ts";
import { loadTokens } from "../load.ts";
import { luminance } from "../color.ts";

/**
 * 토큰 전체를 한 장의 SVG 스펙시트로 생성한다.
 * Figma에 붙여넣으면 편집 가능한 벡터/텍스트 레이어로 들어간다. (dist/tokens-figma.svg)
 */
const W = 1380;
const MX = 48;
const COLS = 8;
const CARD_W = 150;
const CARD_H = 52;
const LABEL_H = 30;
const GAP_X = 12;
const GAP_Y = 18;
const SECTION_GAP = 34;
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

interface Card { label: string; value: string; }

export function emitFigmaSvg(): string {
	const model = normalize();
	const t = loadTokens();
	const body: string[] = [];
	let y = 92;

	const textFor = (hex: string) => {
		const L = luminance(hex);
		return Number.isNaN(L) ? "#1E1E1E" : L > 0.5 ? "#1E1E1E" : "#FFFFFF";
	};

	const sectionTitle = (title: string, count?: number) => {
		body.push(`<text x="${MX}" y="${y}" font-size="18" font-weight="700" fill="#1E1E1E">${esc(title)}${count != null ? `  <tspan font-size="12" font-weight="400" fill="#9E9E9E">(${count})</tspan>` : ""}</text>`);
		y += 22;
	};

	const colorGrid = (cards: Card[]) => {
		cards.forEach((c, i) => {
			const col = i % COLS, row = Math.floor(i / COLS);
			const x = MX + col * (CARD_W + GAP_X);
			const cy = y + row * (CARD_H + LABEL_H + GAP_Y);
			const isLight = (luminance(c.value) || 0) > 0.85;
			body.push(`<rect x="${x}" y="${cy}" width="${CARD_W}" height="${CARD_H}" rx="6" fill="${c.value}" ${isLight ? 'stroke="#EDEDED"' : ""}/>`);
			body.push(`<text x="${x}" y="${cy + CARD_H + 14}" font-size="11" font-weight="600" fill="#1E1E1E">${esc(c.label)}</text>`);
			body.push(`<text x="${x}" y="${cy + CARD_H + 27}" font-size="10" fill="#888888" font-family="monospace">${esc(c.value)}</text>`);
		});
		const rows = Math.ceil(cards.length / COLS);
		y += rows * (CARD_H + LABEL_H + GAP_Y) + SECTION_GAP;
	};

	// --- 색상 그룹 (정규화 모델에서 group별로) ---
	const groupOrder = ["brand", "primitive", "text", "background", "border", "icon", "action", "metric", "chart", "topic", "status", "info", "highlight", "event", "overlay", "landing"];
	const titles: Record<string, string> = {
		brand: "Brand", primitive: "Primitive", text: "Text", background: "Background",
		border: "Border", icon: "Icon", action: "Action", metric: "Metric", chart: "Chart",
		topic: "Topic", status: "Status", info: "Info", highlight: "Highlight", event: "Event",
		overlay: "Overlay", landing: "Landing",
	};
	const colorLeaves = model.leaves.filter((l) => l.type === "color" && typeof l.value === "string");
	for (const g of groupOrder) {
		const cards = colorLeaves
			.filter((l) => l.group === g)
			.map((l) => ({ label: l.path.replace(`color.${g}.`, "").replace("color.", ""), value: l.value as string }));
		if (!cards.length) continue;
		sectionTitle(titles[g] ?? g, cards.length);
		colorGrid(cards);
	}

	// --- Typography (역할 기반 textStyles) ---
	sectionTitle("Typography — Pretendard (textStyles)", Object.keys(t.textStyles).length);
	Object.entries(t.textStyles).forEach(([role, s]) => {
		const px = parseFloat(s.fontSize);
		body.push(`<text x="${MX}" y="${y + px}" font-size="${px}" font-weight="${s.fontWeight}" fill="#1E1E1E">${esc(role)} — 특허 명세서 AI 123</text>`);
		body.push(`<text x="${MX + 560}" y="${y + px}" font-size="11" fill="#888888" font-family="monospace">${esc(s.fontSize)} · w${s.fontWeight} · lh${s.lineHeight}</text>`);
		y += px + 18;
	});
	y += SECTION_GAP;

	// --- Spacing ---
	sectionTitle("Spacing", undefined);
	Object.entries(t.spacing).forEach(([name, v], i) => {
		const px = parseFloat(v);
		const cy = y + i * 22;
		body.push(`<rect x="${MX + 70}" y="${cy}" width="${Math.max(px, 1)}" height="14" fill="#3361BE"/>`);
		body.push(`<text x="${MX}" y="${cy + 12}" font-size="11" fill="#1E1E1E">${esc(name)} · ${esc(v)}</text>`);
	});
	y += Object.keys(t.spacing).length * 22 + SECTION_GAP;

	// --- Radius ---
	sectionTitle("Radius", undefined);
	Object.entries(t.radius).forEach(([name, v], i) => {
		const x = MX + i * 130;
		const rx = Math.min(parseFloat(v), 32);
		body.push(`<rect x="${x}" y="${y}" width="72" height="72" rx="${rx}" fill="#EBF0FA" stroke="#3361BE"/>`);
		body.push(`<text x="${x}" y="${y + 90}" font-size="11" fill="#1E1E1E">${esc(name)} · ${esc(v)}</text>`);
	});
	y += 90 + SECTION_GAP;

	// --- Shadow ---
	sectionTitle("Shadow", undefined);
	const shadowDefs: string[] = [];
	Object.entries(t.shadow).forEach(([name, v], i) => {
		const col = i % 4, row = Math.floor(i / 4);
		const x = MX + col * 320;
		const cy = y + row * 110;
		const m = String(v).match(/(-?\d+)px\s+(-?\d+)px\s+(-?\d+)px(?:\s+(-?\d+)px)?\s+(rgba?\([^)]+\))/);
		let filter = "";
		if (m) {
			const id = `sh-${i}`;
			shadowDefs.push(`<filter id="${id}" x="-50%" y="-50%" width="200%" height="200%"><feDropShadow dx="${m[1]}" dy="${m[2]}" stdDeviation="${Math.max(parseInt(m[3]) / 2, 1)}" flood-color="${m[5]}"/></filter>`);
			filter = ` filter="url(#${id})"`;
		}
		body.push(`<rect x="${x}" y="${cy}" width="120" height="60" rx="8" fill="#FFFFFF" stroke="#F0F0F0"${filter}/>`);
		body.push(`<text x="${x + 132}" y="${cy + 22}" font-size="12" font-weight="600" fill="#1E1E1E">${esc(name)}</text>`);
		body.push(`<text x="${x + 132}" y="${cy + 38}" font-size="9" fill="#888888" font-family="monospace">${esc(String(v).slice(0, 30))}</text>`);
	});
	y += Math.ceil(Object.keys(t.shadow).length / 4) * 110 + 40;

	const H = y;
	return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Pretendard, sans-serif">
<defs>${shadowDefs.join("")}</defs>
<rect width="${W}" height="${H}" fill="#FFFFFF"/>
<text x="${MX}" y="48" font-size="28" font-weight="800" fill="#1E1E1E">PatSol Design Tokens</text>
<text x="${MX}" y="70" font-size="13" fill="#757575">designTokens-v0.2 · brand primary #3361BE · 생성: token-harness</text>
${body.join("\n")}
</svg>
`;
}

import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import type { NormalizedModel } from "../model.ts";
import { deltaE } from "../color.ts";
import { componentSpecs } from "./pairs.ts";

const HERE = dirname(fileURLToPath(import.meta.url));
const MEASURED = resolve(HERE, "../../dist/measured.json");

export interface MeasuredFile {
	live?: Record<string, Record<string, string>>;
	figma?: Record<string, Record<string, string>>;
}

export interface SuggestRow {
	component: string;
	prop: string;
	figma?: string; // 디자인 의도
	live?: string; // 실제 구현
	expectedToken?: string; // 기대 토큰 경로 + 값
	recommended?: string; // 권장 토큰 (ΔE 최소)
}

function nearestToken(model: NormalizedModel, value: string): { path: string; dE: number } | null {
	let best: { path: string; dE: number } | null = null;
	for (const leaf of model.leaves) {
		if (leaf.type !== "color" || typeof leaf.value !== "string") continue;
		if (leaf.group !== "primitive" && !leaf.path.startsWith("color.")) continue;
		const d = deltaE(value, leaf.value);
		if (!best || d < best.dE) best = { path: leaf.path, dE: d };
	}
	return best;
}

export function loadMeasured(): MeasuredFile | null {
	if (!existsSync(MEASURED)) return null;
	try {
		return JSON.parse(readFileSync(MEASURED, "utf8")) as MeasuredFile;
	} catch {
		return null;
	}
}

const PROP_TO_EXPECT: Record<string, "color" | "background" | "border"> = {
	color: "color",
	backgroundColor: "background",
	borderColor: "border",
};

export function buildSuggestions(model: NormalizedModel): SuggestRow[] {
	const measured = loadMeasured();
	if (!measured) return [];
	const rows: SuggestRow[] = [];
	for (const spec of componentSpecs) {
		const live = measured.live?.[spec.component] ?? {};
		const figma = measured.figma?.[spec.component] ?? {};
		for (const prop of spec.props) {
			const liveVal = live[prop];
			const figmaVal = figma[prop] ?? figma.fill ?? figma.stroke;
			if (!liveVal && !figmaVal) continue;
			const expectKey = PROP_TO_EXPECT[prop];
			const expectPath = expectKey ? spec.expects[expectKey] : undefined;
			const expectVal = expectPath ? model.byPath[expectPath] : undefined;
			const probe = liveVal ?? figmaVal!;
			const isColor = typeof probe === "string" && /^(#|rgb)/i.test(probe.trim());
			const nearRaw = isColor ? nearestToken(model, probe) : null;
			const near = nearRaw && Number.isFinite(nearRaw.dE) ? nearRaw : null;
			rows.push({
				component: spec.component,
				prop,
				figma: figmaVal,
				live: liveVal,
				expectedToken: expectPath ? `${expectPath} (${expectVal ?? "?"})` : undefined,
				recommended: near ? `${near.path} (ΔE ${near.dE.toFixed(1)})` : undefined,
			});
		}
	}
	return rows;
}

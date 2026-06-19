/**
 * Figma 변수 동기화 (opt-in). docs/harness/figma_sync.md 참조.
 * 경로 우선순위: FIGMA_API_KEY REST → Dev Mode MCP(수동) → stub.
 * 키/토큰은 환경변수로만 사용하고 출력에 남기지 않는다.
 */
import type { NormalizedModel } from "../model.ts";
import { deltaE } from "../color.ts";

const FILE_KEY = "XD5TxmzMB68uXpKRmrgHpt"; // Patsol_StoryBoard

export interface SyncResult {
	available: boolean;
	source: "rest" | "mcp" | "none";
	note: string;
	diff?: Array<{ kind: "code-only" | "figma-only" | "mismatch"; name: string; code?: string; figma?: string; deltaE?: number }>;
}

async function fetchFigmaVariables(key: string): Promise<Record<string, string>> {
	const res = await fetch(`https://api.figma.com/v1/files/${FILE_KEY}/variables/local`, {
		headers: { "X-Figma-Token": key },
	});
	if (!res.ok) throw new Error(`Figma API ${res.status}`);
	const json = (await res.json()) as { meta?: { variables?: Record<string, unknown> } };
	const out: Record<string, string> = {};
	const vars = json.meta?.variables ?? {};
	for (const v of Object.values(vars) as Array<Record<string, unknown>>) {
		const name = String(v.name ?? "");
		const values = (v.valuesByMode ?? {}) as Record<string, unknown>;
		const first = Object.values(values)[0];
		if (first && typeof first === "object" && "r" in (first as object)) {
			const c = first as { r: number; g: number; b: number };
			const hex = `#${[c.r, c.g, c.b].map((x) => Math.round(x * 255).toString(16).padStart(2, "0")).join("")}`;
			out[name] = hex;
		}
	}
	return out;
}

export async function syncFigma(model: NormalizedModel): Promise<SyncResult> {
	const key = process.env.FIGMA_API_KEY;
	if (!key) {
		return {
			available: false,
			source: "none",
			note:
				"FIGMA_API_KEY 미설정 → REST 경로 비활성. Figma Dev Mode MCP(get_variable_defs)가 연결돼 있으면 " +
				"수동으로 변수를 끌어와 dist/measured.json 또는 sync 입력으로 전달하세요.",
		};
	}
	try {
		const figmaVars = await fetchFigmaVariables(key);
		const codeColors = new Map<string, string>();
		for (const leaf of model.leaves) {
			if (leaf.type === "color" && typeof leaf.value === "string") {
				codeColors.set(leaf.path.split(".").pop()!, leaf.value);
			}
		}
		const diff: NonNullable<SyncResult["diff"]> = [];
		for (const [name, fHex] of Object.entries(figmaVars)) {
			const short = name.split("/").pop()!;
			const code = codeColors.get(short);
			if (!code) diff.push({ kind: "figma-only", name, figma: fHex });
			else {
				const d = deltaE(code, fHex);
				if (d > 1) diff.push({ kind: "mismatch", name, code, figma: fHex, deltaE: Number(d.toFixed(1)) });
			}
		}
		return { available: true, source: "rest", note: `Figma 변수 ${Object.keys(figmaVars).length}개 대조`, diff };
	} catch (e) {
		return { available: false, source: "none", note: `Figma REST 실패: ${(e as Error).message}` };
	}
}

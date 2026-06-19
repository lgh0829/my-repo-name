import type { Finding, NormalizedModel, Severity } from "../model.ts";
import { deltaE } from "../color.ts";
import config from "../../config/harness.config.ts";

/** 가장 가까운 primitive를 ΔE2000으로 찾는다. */
function nearestPrimitive(
	model: NormalizedModel,
	value: string,
): { path: string; dE: number } | null {
	let best: { path: string; dE: number } | null = null;
	for (const [, paths] of Object.entries(model.hexToPrimitive)) {
		const p = paths[0];
		const primValue = model.byPath[p];
		if (typeof primValue !== "string") continue;
		const d = deltaE(value, primValue);
		if (!best || d < best.dE) best = { path: p, dE: d };
	}
	return best;
}

/** semantic 레이어에 primitive 미경유 하드코딩 hex가 박혀 있으면 신고. */
export function checkHardcodedHex(model: NormalizedModel): Finding[] {
	const out: Finding[] = [];
	const { severityByGroup, nearPrimitiveDeltaE } = config.hardcoded;
	for (const leaf of model.leaves) {
		if (leaf.type !== "color" || typeof leaf.value !== "string") continue;
		if (leaf.group === "primitive" || leaf.group === "brand") continue;
		if (leaf.refOf !== null) continue; // primitive로 추적됨 → 정상

		const severity: Severity = severityByGroup[leaf.group] ?? "warn";
		const near = nearestPrimitive(model, leaf.value);
		let suggestion: string;
		if (near && near.dE < nearPrimitiveDeltaE) {
			suggestion = `${near.path}(ΔE ${near.dE.toFixed(1)})로 교체 권장`;
		} else {
			suggestion = near
				? `유사 primitive 없음(최근접 ${near.path} ΔE ${near.dE.toFixed(1)}) → primitive 신규 등록 후 참조`
				: "primitive 신규 등록 후 참조";
		}
		out.push({
			rule: "hardcoded-hex",
			severity,
			path: leaf.path,
			message: `하드코딩 hex ${leaf.value} (primitive 미경유) — ${suggestion}`,
			data: { value: leaf.value, group: leaf.group, nearest: near?.path, deltaE: near?.dE },
		});
	}
	return out;
}

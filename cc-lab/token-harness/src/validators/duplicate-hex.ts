import type { Finding, NormalizedModel } from "../model.ts";
import { normHex } from "../color.ts";

/** primitive 레이어 내부에서 같은 hex가 여러 이름으로 존재하면 warn. */
export function checkDuplicateHex(model: NormalizedModel): Finding[] {
	const out: Finding[] = [];
	const groups: Record<string, string[]> = {};
	for (const leaf of model.leaves) {
		if (leaf.type !== "color" || typeof leaf.value !== "string") continue;
		if (!leaf.path.startsWith("color.primitive.")) continue;
		const h = normHex(leaf.value);
		(groups[h] ??= []).push(leaf.path);
	}
	for (const [hex, paths] of Object.entries(groups)) {
		if (paths.length > 1) {
			out.push({
				rule: "duplicate-hex",
				severity: "warn",
				path: paths[0],
				message: `중복 primitive hex ${hex} — ${paths.join(", ")}. 하나로 통합하고 나머지는 alias 권장.`,
				data: { hex, paths },
			});
		}
	}
	return out;
}

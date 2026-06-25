import type { Finding, NormalizedModel } from "../model.ts";
import { normHex } from "../color.ts";
import { parse } from "culori";

/** primitive 레이어 내부에서 같은 hex가 여러 이름으로 존재하면 warn. */
export function checkDuplicateHex(model: NormalizedModel): Finding[] {
	const out: Finding[] = [];
	const groups: Record<string, string[]> = {};
	for (const leaf of model.leaves) {
		if (leaf.type !== "color" || typeof leaf.value !== "string") continue;
		if (!leaf.path.startsWith("color.primitive.")) continue;
		// alpha < 1 인 rgba 값은 solid color와 별도 토큰이므로 중복 검사 제외
		const parsed = parse(leaf.value as string);
		if (parsed && (parsed.alpha ?? 1) < 1) continue;
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

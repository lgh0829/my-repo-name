import type { Finding, NormalizedModel } from "../model.ts";
import config from "../../config/harness.config.ts";

const SCALE = /^[a-z]+[0-9]{2,3}$/;

/** primitive 네이밍: 스케일 패턴 또는 allowlist 외면 warn. */
export function checkNaming(model: NormalizedModel): Finding[] {
	const out: Finding[] = [];
	const seen = new Set<string>();
	for (const leaf of model.leaves) {
		if (!leaf.path.startsWith("color.primitive.")) continue;
		const name = leaf.path.split(".").pop()!;
		if (seen.has(name)) continue;
		seen.add(name);
		if (SCALE.test(name) || (config.namingAllowlist as readonly string[]).includes(name)) continue;
		out.push({
			rule: "naming",
			severity: "warn",
			path: leaf.path,
			message: `비표준 primitive 네이밍 "${name}" — 스케일(예: blue500) 또는 allowlist 등록 권장`,
			data: { name },
		});
	}
	return out;
}

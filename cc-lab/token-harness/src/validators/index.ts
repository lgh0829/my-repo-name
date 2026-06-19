import type { Finding, NormalizedModel, Severity } from "../model.ts";
import { checkContrast } from "./contrast.ts";
import { checkDuplicateHex } from "./duplicate-hex.ts";
import { checkLightnessMonotonic } from "./lightness-monotonic.ts";
import { checkHardcodedHex } from "./hardcoded-hex.ts";
import { checkNaming } from "./naming.ts";
import { checkBrandTone } from "./brand-tone.ts";

export type Rule = (model: NormalizedModel) => Finding[];

export const rules: Record<string, Rule> = {
	contrast: checkContrast,
	"duplicate-hex": checkDuplicateHex,
	"lightness-monotonic": checkLightnessMonotonic,
	"hardcoded-hex": checkHardcodedHex,
	naming: checkNaming,
	"brand-tone": checkBrandTone,
};

export function runAll(model: NormalizedModel): Finding[] {
	const out: Finding[] = [];
	for (const fn of Object.values(rules)) out.push(...fn(model));
	const order: Record<Severity, number> = { error: 0, warn: 1, info: 2 };
	return out.sort((a, b) => order[a.severity] - order[b.severity] || a.rule.localeCompare(b.rule));
}

export function summarize(findings: Finding[]): Record<Severity, number> {
	const c: Record<Severity, number> = { error: 0, warn: 0, info: 0 };
	for (const f of findings) c[f.severity]++;
	return c;
}

import type { Finding, NormalizedModel } from "../model.ts";
import { contrast } from "../color.ts";
import config from "../../config/harness.config.ts";

function resolve(model: NormalizedModel, ref: string): string | null {
	if (ref.startsWith("#") || /^rgb/i.test(ref)) return ref;
	const v = model.byPath[ref];
	return typeof v === "string" ? v : null;
}

export function checkContrast(model: NormalizedModel): Finding[] {
	const out: Finding[] = [];
	const { normalText, largeText } = config.contrast;
	for (const pair of config.pairs) {
		const fg = resolve(model, pair.fg);
		const bg = resolve(model, pair.bg);
		if (!fg || !bg) {
			out.push({
				rule: "contrast",
				severity: "warn",
				path: pair.fg,
				message: `대비 페어 해석 실패: ${pair.fg} / ${pair.bg} (${pair.label})`,
			});
			continue;
		}
		const ratio = contrast(fg, bg);
		const min = pair.large ? largeText : normalText;
		if (Number.isNaN(ratio)) continue;
		if (ratio < min) {
			out.push({
				rule: "contrast",
				severity: pair.large ? "warn" : "error",
				path: pair.fg,
				message: `대비 부족 ${ratio.toFixed(2)}:1 < ${min}:1 — ${pair.label} (${fg} on ${bg})`,
				data: { ratio: Number(ratio.toFixed(2)), min, fg, bg, against: pair.bg },
			});
		}
	}
	return out;
}

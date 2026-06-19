import type { Finding, NormalizedModel } from "../model.ts";
import { oklchOf, hueDistance } from "../color.ts";
import config from "../../config/harness.config.ts";

function isBrandExpected(path: string): boolean {
	const { includes, prefixes, excludePrefixes } = config.brandExpectedMatch;
	if (excludePrefixes.some((p) => path.startsWith(p))) return false;
	if (prefixes.some((p) => path.startsWith(p))) return true;
	return includes.some((s) => path.toLowerCase().includes(s.toLowerCase()));
}

/** 브랜드 블루여야 하는 토큰이 기준 hue 밴드를 벗어나면 warn. */
export function checkBrandTone(model: NormalizedModel): Finding[] {
	const out: Finding[] = [];
	const ref = oklchOf(config.brand.keyHex);
	if (!ref) return out;
	const { hueBand, minChroma } = config.brand;

	for (const leaf of model.leaves) {
		if (leaf.type !== "color" || typeof leaf.value !== "string") continue;
		if (leaf.group === "primitive") continue;
		if (!isBrandExpected(leaf.path)) continue;
		const c = oklchOf(leaf.value);
		if (!c) continue;
		const hueOff = hueDistance(c.h, ref.h);
		const lowChroma = !Number.isNaN(c.c) && c.c < minChroma;
		if (lowChroma || (!Number.isNaN(hueOff) && hueOff > hueBand)) {
			out.push({
				rule: "brand-tone",
				severity: "warn",
				path: leaf.path,
				message:
					`브랜드톤 이탈: ${leaf.value} (hue 차이 ${Number.isNaN(hueOff) ? "?" : hueOff.toFixed(0)}°` +
					`, 기준 ±${hueBand}°${lowChroma ? ", 저채도" : ""})`,
				data: { value: leaf.value, hueOffset: hueOff, refHue: ref.h, chroma: c.c },
			});
		}
	}
	return out;
}

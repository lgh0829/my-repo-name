import type { Finding, NormalizedModel } from "../model.ts";
import { lightness } from "../color.ts";
import config from "../../config/harness.config.ts";

interface GrayEntry {
	name: string;
	n: number;
	value: string;
	l: number;
}

function isException(a: string, b: string): boolean {
	return config.lightnessExceptions.some(
		([x, y]) => (x === a && y === b) || (x === b && y === a),
	);
}

/** grayN 스케일: 숫자가 클수록 어두워야 한다(oklch l 단조 감소). */
export function checkLightnessMonotonic(model: NormalizedModel): Finding[] {
	const out: Finding[] = [];
	const grays: GrayEntry[] = [];
	for (const leaf of model.leaves) {
		if (!leaf.path.startsWith("color.primitive.")) continue;
		const name = leaf.path.split(".").pop()!;
		if ((config.lightnessExcludeNames as readonly string[]).includes(name)) continue;
		const m = /^gray(\d+)$/.exec(name);
		if (!m || typeof leaf.value !== "string") continue;
		grays.push({ name, n: Number(m[1]), value: leaf.value, l: lightness(leaf.value) });
	}
	grays.sort((a, b) => a.n - b.n);
	for (let i = 1; i < grays.length; i++) {
		const prev = grays[i - 1];
		const cur = grays[i];
		// cur 숫자가 더 크므로 cur.l 이 prev.l 보다 작아야(더 어두워야) 함
		if (cur.l > prev.l + 1e-4) {
			const exc = isException(prev.name, cur.name);
			out.push({
				rule: "lightness-monotonic",
				severity: exc ? "info" : "error",
				path: `color.primitive.${cur.name}`,
				message:
					`명도 역전: ${cur.name}(${cur.value}, l=${cur.l.toFixed(3)})이 ` +
					`${prev.name}(${prev.value}, l=${prev.l.toFixed(3)})보다 밝음` +
					(exc ? " [예외: 의도된 역할 분리]" : ""),
				data: { darker: prev.name, lighter: cur.name, exception: exc },
			});
		}
	}
	return out;
}

import { loadTokens } from "./load.ts";
import { isColorString, normHex } from "./color.ts";
import type { NormalizedModel, TokenLeaf, TokenType } from "./model.ts";

function classify(path: string, value: string | number): TokenType {
	if (typeof value === "number") {
		return path.includes("fontWeight") ? "fontWeight" : "number";
	}
	const v = value.trim();
	if (isColorString(v)) return "color";
	if (/^-?[\d.]+px$/.test(v)) return "dimension";
	if (path.includes("shadow") || /\d+px .*rgba?\(/.test(v)) return "shadow";
	if (path.includes("fontFamily")) return "fontFamily";
	return "other";
}

/** color 토큰은 'color' 다음 세그먼트, 그 외 top-level 세그먼트. */
function groupOf(path: string): string {
	const parts = path.split(".");
	if (parts[0] === "color") return parts[1] ?? "color";
	return parts[0] ?? "";
}

function walk(
	node: unknown,
	prefix: string,
	out: Array<{ path: string; value: string | number }>,
): void {
	if (node === null || node === undefined) return;
	if (typeof node === "string" || typeof node === "number") {
		out.push({ path: prefix, value: node });
		return;
	}
	if (Array.isArray(node)) {
		node.forEach((v, i) => walk(v, `${prefix}.${i}`, out));
		return;
	}
	if (typeof node === "object") {
		for (const [k, v] of Object.entries(node as Record<string, unknown>)) {
			walk(v, prefix ? `${prefix}.${k}` : k, out);
		}
	}
}

export function normalize(): NormalizedModel {
	const raw = loadTokens();
	const flat: Array<{ path: string; value: string | number }> = [];
	walk(raw, "", flat);

	// primitive/brand hex 역색인
	const hexToPrimitive: Record<string, string[]> = {};
	for (const { path, value } of flat) {
		const isPrim = path.startsWith("color.primitive.") || path.startsWith("color.brand.");
		if (isPrim && typeof value === "string" && isColorString(value)) {
			const h = normHex(value);
			(hexToPrimitive[h] ??= []).push(path);
		}
	}

	const leaves: TokenLeaf[] = [];
	const byPath: Record<string, string | number> = {};
	for (const { path, value } of flat) {
		byPath[path] = value;
		const type = classify(path, value);
		const group = groupOf(path);
		let refOf: string | null = null;
		if (type === "color" && typeof value === "string") {
			const h = normHex(value);
			const matches = hexToPrimitive[h];
			if (matches && matches.length) {
				// 자기 자신(primitive) 제외하고 첫 매칭
				refOf = matches.find((p) => p !== path) ?? (group === "primitive" ? null : matches[0]);
			}
		}
		leaves.push({ path, value, type, group, refOf });
	}

	return { leaves, byPath, hexToPrimitive };
}

export default normalize;

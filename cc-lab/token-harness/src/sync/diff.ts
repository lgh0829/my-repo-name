import type { NormalizedModel } from "../model.ts";
import { deltaE, isColorString, normHex } from "../color.ts";
import config from "../../config/harness.config.ts";

export interface MappedEntry {
	name: string;
	codePath: string;
	figma: string;
	code: string;
	deltaE: number;
	verdict: "일치" | "불일치";
}

export interface ValueEntry {
	name: string;
	figma: string;
	nearestPath: string;
	nearestValue: string;
	deltaE: number;
	verdict: "동일" | "유사" | "코드에 없음";
}

export interface DiffResult {
	mapped: MappedEntry[];
	value: ValueEntry[];
}

function colorLeaves(model: NormalizedModel): Array<{ path: string; value: string }> {
	return model.leaves
		.filter((l) => l.type === "color" && typeof l.value === "string")
		.map((l) => ({ path: l.path, value: l.value as string }));
}

/** Figma 변수맵을 SSOT와 대조. 이름 자동매칭은 네이밍 체계가 달라 쓰지 않고, 명시 매핑 + 값(ΔE) 기반. */
export function diffVariables(model: NormalizedModel, figmaVars: Record<string, string>): DiffResult {
	const leaves = colorLeaves(model);
	const byPath = new Map(leaves.map((l) => [l.path, l.value]));
	const { near, similar } = config.figmaDiff;
	const map = config.figmaMap as Record<string, string>;

	const mapped: MappedEntry[] = [];
	const value: ValueEntry[] = [];

	for (const [name, rawVal] of Object.entries(figmaVars)) {
		if (!isColorString(rawVal)) continue;
		const fHex = normHex(rawVal);

		if (map[name]) {
			const codePath = map[name];
			const codeVal = byPath.get(codePath);
			if (codeVal) {
				const d = deltaE(codeVal, rawVal);
				mapped.push({
					name, codePath, figma: fHex, code: normHex(codeVal),
					deltaE: Number(d.toFixed(1)), verdict: d <= near ? "일치" : "불일치",
				});
				continue;
			}
		}

		// 값 기반: 최근접 코드 토큰
		let best: { path: string; value: string; d: number } | null = null;
		for (const l of leaves) {
			const d = deltaE(rawVal, l.value);
			if (!best || d < best.d) best = { path: l.path, value: l.value, d };
		}
		const d = best?.d ?? Infinity;
		value.push({
			name, figma: fHex,
			nearestPath: best?.path ?? "—",
			nearestValue: best ? normHex(best.value) : "—",
			deltaE: Number(d.toFixed(1)),
			verdict: d <= near ? "동일" : d <= similar ? "유사" : "코드에 없음",
		});
	}
	value.sort((a, b) => a.deltaE - b.deltaE);
	return { mapped, value };
}

export function renderDiff(res: DiffResult, note: string): string {
	const { mapped, value } = res;
	const mism = mapped.filter((m) => m.verdict === "불일치").length;
	const absent = value.filter((v) => v.verdict === "코드에 없음").length;
	const same = value.filter((v) => v.verdict === "동일").length;
	const sim = value.filter((v) => v.verdict === "유사").length;
	const L: string[] = [];
	L.push("# Figma ↔ 코드 변수 diff");
	L.push("");
	L.push(`> ${note}`);
	L.push("> 네이밍 체계가 달라(Figma \`color/primary/500\` vs 코드 \`brand.primary\`) 이름 자동매칭 대신 **명시 매핑 + 값(ΔE2000) 기반**으로 대조한다.");
	L.push("");
	L.push(`**요약**: 매핑 불일치 🔴${mism} · 값기반 동일 ✅${same} / 유사 🟡${sim} / 코드에 없음 🔵${absent}`);
	L.push("");

	L.push("## 1. 명시 매핑 대조 (브랜드·핵심 토큰)");
	L.push("");
	if (mapped.length) {
		L.push("| Figma 변수 | 코드 토큰 | Figma | 코드 | ΔE | 판정 |");
		L.push("|---|---|---|---|---|---|");
		for (const m of mapped) {
			const icon = m.verdict === "일치" ? "✅" : "🔴";
			L.push(`| ${m.name} | \`${m.codePath}\` | ${m.figma} | ${m.code} | ${m.deltaE} | ${icon} ${m.verdict} |`);
		}
	} else L.push("_매핑 없음 (config.figmaMap)_");
	L.push("");

	L.push("## 2. 값 기반 대조 (Figma 변수별 최근접 코드 토큰)");
	L.push("");
	L.push("| Figma 변수 | Figma 값 | 최근접 코드 토큰 | 코드 값 | ΔE | 판정 |");
	L.push("|---|---|---|---|---|---|");
	for (const v of value) {
		const icon = v.verdict === "동일" ? "✅" : v.verdict === "유사" ? "🟡" : "🔵";
		L.push(`| ${v.name} | ${v.figma} | \`${v.nearestPath}\` | ${v.nearestValue} | ${v.deltaE} | ${icon} ${v.verdict} |`);
	}
	L.push("");
	L.push("> 🔵 코드에 없음 = Figma에만 존재하는 값. 토큰화하거나 Figma에서 정리 대상.");
	L.push("");
	return L.join("\n");
}

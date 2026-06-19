import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, relative } from "node:path";
import { normalize } from "../normalize.ts";
import { deltaE, normHex } from "../color.ts";
import config from "../../config/harness.config.ts";

/** 자주 새는 Tailwind 기본 팔레트(표기용, 판단은 보류). */
const TAILWIND_DEFAULTS = new Set([
	"#f9fafb", "#f3f4f6", "#e5e7eb", "#d1d5db", "#9ca3af", "#6b7280",
	"#4b5563", "#374151", "#1f2937", "#111827", "#030712",
	"#ef4444", "#22c55e", "#3b82f6", "#2563eb", "#60a5fa",
]);

const HEX = /#[0-9a-fA-F]{6}\b/g;
const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build", ".next", "coverage", "storybook-static"]);
const EXTS = [".ts", ".tsx", ".css", ".scss"];

function walk(dir: string, out: string[] = []): string[] {
	for (const name of readdirSync(dir)) {
		if (SKIP_DIRS.has(name)) continue;
		const p = join(dir, name);
		const st = statSync(p);
		if (st.isDirectory()) walk(p, out);
		else if (EXTS.some((e) => name.endsWith(e))) out.push(p);
	}
	return out;
}

/** 매칭 직전 텍스트로 CSS 속성/Tailwind 유틸리티를 추정해 사용 맥락 라벨을 만든다. */
function usageLabel(before: string): string {
	const tw = before.match(/\b(bg|text|border|ring|fill|stroke|shadow|from|to|via|decoration|outline|caret|accent|divide|placeholder)-\[#?[0-9a-fA-F]*$/);
	const raw = tw ? tw[1] : (before.match(/([A-Za-z][\w-]*)\s*[:=]\s*["'`(\s]*$/)?.[1] ?? "");
	const c = raw.toLowerCase();
	if (/^(background|bg|bgcolor|backgroundcolor)$/.test(c) || /background/.test(c)) return "배경";
	if (/^(color|text|textcolor|fill)$/.test(c) || /textfillcolor|fontcolor/.test(c)) return "텍스트/fill";
	if (/border|outline|ring|divide/.test(c)) return "보더";
	if (/shadow/.test(c)) return "그림자";
	if (/stroke/.test(c)) return "stroke";
	if (/from|to|via|gradient/.test(c)) return "그라데이션";
	if (!c) return "기타(값만)";
	return `키:${raw}`; // 커스텀 키명(상수/테마 정의)으로 추정
}

export type Action = "use-token" | "merge" | "new";
export interface Occurrence { file: string; line: number; usage: string; system: string; }

/** 해당 라인의 스타일 시스템 추정: tailwind / mui / css / js(상수·객체 정의). */
function systemOf(file: string, line: string, before: string): string {
	if (/\.(css|scss)$/.test(file)) return "css";
	if (/\b(bg|text|border|ring|fill|stroke|shadow|from|to|via|decoration|outline|caret|accent|divide|placeholder)-\[#?[0-9a-fA-F]*$/.test(before)) return "tailwind";
	if (/class(Name)?\s*=/.test(line) && /\[#/.test(line)) return "tailwind";
	if (/\b(sx|styled|createTheme|bgcolor|palette|theme\.)\b/.test(line) || /\b(backgroundColor|borderColor|boxShadow|borderColor)\s*:/.test(line)) return "mui";
	return "js"; // const/object 값 정의 등
}
export interface HexRow {
	hex: string;
	count: number;
	action: Action;
	token: string | null;      // colorTokens.* 참조
	tokenHex: string | null;   // 권장 토큰의 실제 hex
	deltaE: number;
	tailwind: boolean;
	usages: Record<string, number>;  // 사용 맥락 → 횟수
	files: Record<string, number>;   // 발견 파일(상대경로) → 횟수
	systems: Record<string, number>; // 스타일 시스템 → 횟수
	occ: Occurrence[];
}

const refOf = (path: string) => path.replace(/^color\./, "colorTokens.");

export function auditProductColors(srcDir: string): { rows: HexRow[]; fileCount: number } {
	if (!existsSync(srcDir)) throw new Error(`경로 없음: ${srcDir}`);
	const model = normalize();
	const colors = model.leaves.filter((l) => l.type === "color" && typeof l.value === "string") as Array<{ path: string; value: string }>;
	const exact = new Map<string, string>();
	for (const l of colors) {
		const h = normHex(l.value);
		const isPrim = l.path.startsWith("color.primitive.") || l.path.startsWith("color.brand.");
		if (!exact.has(h) || isPrim) exact.set(h, l.path);
	}
	const hexOfPath = (path: string) => {
		const v = model.byPath[path];
		return typeof v === "string" ? normHex(v) : null;
	};

	const exclude = config.auditExclude as readonly string[];
	const isExcluded = (rel: string) => exclude.some((e) => rel === e || rel.endsWith(`/${e}`) || rel.endsWith(e));
	const files = walk(srcDir).filter((f) => !isExcluded(relative(srcDir, f)));
	const occ = new Map<string, Occurrence[]>();
	for (const f of files) {
		const rel = relative(srcDir, f);
		readFileSync(f, "utf8").split(/\r?\n/).forEach((ln, i) => {
			let m: RegExpExecArray | null;
			HEX.lastIndex = 0;
			while ((m = HEX.exec(ln)) !== null) {
				const h = normHex(m[0]);
				const before = ln.slice(0, m.index);
				const usage = usageLabel(before);
				const system = systemOf(rel, ln, before);
				(occ.get(h) ?? occ.set(h, []).get(h)!).push({ file: rel, line: i + 1, usage, system });
			}
		});
	}

	const rows: HexRow[] = [];
	for (const [hex, occs] of occ) {
		const usages: Record<string, number> = {};
		const filesAgg: Record<string, number> = {};
		const systems: Record<string, number> = {};
		for (const o of occs) {
			usages[o.usage] = (usages[o.usage] ?? 0) + 1;
			filesAgg[o.file] = (filesAgg[o.file] ?? 0) + 1;
			systems[o.system] = (systems[o.system] ?? 0) + 1;
		}
		const tw = TAILWIND_DEFAULTS.has(hex);
		let action: Action, tokenPath: string | null, d = 0;
		if (exact.has(hex)) { action = "use-token"; tokenPath = exact.get(hex)!; }
		else {
			let best: { p: string; d: number } | null = null;
			for (const l of colors) { const dd = deltaE(hex, l.value); if (!best || dd < best.d) best = { p: l.path, d: dd }; }
			d = best ? Number(best.d.toFixed(1)) : 99;
			tokenPath = best ? best.p : null;
			action = best && best.d < 2 ? "merge" : "new";
		}
		rows.push({
			hex, count: occs.length, action,
			token: tokenPath ? refOf(tokenPath) : null,
			tokenHex: tokenPath ? hexOfPath(tokenPath) : null,
			deltaE: d, tailwind: tw, usages, files: filesAgg, systems, occ: occs,
		});
	}
	rows.sort((a, b) => b.count - a.count);
	return { rows, fileCount: files.length };
}

const usageStr = (u: Record<string, number>) =>
	Object.entries(u).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}×${v}`).join(", ");

const base = (p: string) => p.split("/").pop() ?? p;
const filesStr = (f: Record<string, number>) => {
	const ents = Object.entries(f).sort((a, b) => b[1] - a[1]);
	const top = ents.slice(0, 3).map(([p, v]) => `${base(p)}(${v})`).join(", ");
	return ents.length > 3 ? `${top} +${ents.length - 3}` : top;
};
const systemsStr = (s: Record<string, number>) =>
	Object.entries(s).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k}×${v}`).join(", ");

export function renderAudit(rows: HexRow[], fileCount: number, srcDir: string): string {
	const sum = (a: Action) => rows.filter((r) => r.action === a).reduce((n, r) => n + r.count, 0);
	const distinct = (a: Action) => rows.filter((r) => r.action === a).length;
	const L: string[] = [];
	L.push("# 제품 색상 감사 — 매핑표 + 치환계획");
	L.push("");
	L.push(`> 대상: \`${srcDir}\` (${fileCount} 파일) · SSOT: designTokens-v0.2 · 생성: token-harness audit-product`);
	L.push(`> 제외: ${(config.auditExclude as readonly string[]).map((e) => `\`${e}\``).join(", ")}`);
	L.push("");
	L.push(`**distinct ${rows.length}종 / 등장 ${rows.reduce((n, r) => n + r.count, 0)}회**`);
	L.push(`- ✅ 이미 토큰값(참조만 교체): ${distinct("use-token")}종 / ${sum("use-token")}회`);
	L.push(`- 🟡 ΔE<2 병합: ${distinct("merge")}종 / ${sum("merge")}회`);
	L.push(`- 🔵 신규(토큰 정의 필요): ${distinct("new")}종 / ${sum("new")}회`);
	L.push("");

	const tbl = (title: string, a: Action) => {
		const rs = rows.filter((r) => r.action === a);
		L.push(`## ${title} (${rs.length}종)`);
		L.push("");
		L.push("| 제품 hex | ×회 | 권장 토큰 | 권장 hex | ΔE | 시스템 | 사용 맥락 | 발견 파일 | 비고 |");
		L.push("|---|---|---|---|---|---|---|---|---|");
		for (const r of rs) {
			const note = r.tailwind ? "⚠ Tailwind 기본값" : "";
			L.push(`| \`${r.hex}\` | ${r.count} | ${r.token ? `\`${r.token}\`` : "—"} | ${r.tokenHex ? `\`${r.tokenHex}\`` : "—"} | ${r.deltaE} | ${systemsStr(r.systems)} | ${usageStr(r.usages)} | ${filesStr(r.files)} | ${note} |`);
		}
		L.push("");
	};
	tbl("✅ 토큰 참조로 교체 (값 동일)", "use-token");
	tbl("🟡 기존 토큰으로 병합 (ΔE<2)", "merge");
	tbl("🔵 신규 — 토큰 정의 후 참조 (또는 제거 통일)", "new");

	L.push("## 파일별 치환 계획 (값 동일·병합분 — 즉시 치환 가능)");
	L.push("");
	const byFile = new Map<string, Array<{ line: number; hex: string; token: string; tokenHex: string | null; usage: string }>>();
	for (const r of rows) {
		if (r.action === "new" || !r.token) continue;
		for (const o of r.occ) (byFile.get(o.file) ?? byFile.set(o.file, []).get(o.file)!).push({ line: o.line, hex: r.hex, token: r.token, tokenHex: r.tokenHex, usage: o.usage });
	}
	for (const [file, items] of [...byFile.entries()].sort()) {
		items.sort((a, b) => a.line - b.line);
		L.push(`### ${file}`);
		for (const it of items) L.push(`- L${it.line} [${it.usage}]: \`${it.hex}\` → \`${it.token}\` (${it.tokenHex})`);
		L.push("");
	}
	return L.join("\n");
}

import type { Finding, Severity } from "../model.ts";
import { summarize } from "../validators/index.ts";
import type { SuggestRow } from "../measure/suggest.ts";

const ICON: Record<Severity, string> = { error: "🔴", warn: "🟡", info: "🔵" };

export function renderReport(findings: Finding[], suggestions: SuggestRow[]): string {
	const c = summarize(findings);
	const lines: string[] = [];
	lines.push("# PatSol 디자인 토큰 검증 리포트");
	lines.push("");
	lines.push(`> SSOT: \`design/designTokens-v0.2.ts\` · 브랜드 기준 primary \`#3361BE\``);
	lines.push("");
	lines.push(`**요약**: 🔴 error ${c.error} · 🟡 warn ${c.warn} · 🔵 info ${c.info}`);
	lines.push("");

	const byRule = new Map<string, Finding[]>();
	for (const f of findings) {
		if (!byRule.has(f.rule)) byRule.set(f.rule, []);
		byRule.get(f.rule)!.push(f);
	}

	lines.push("## 규칙별 결과");
	lines.push("");
	for (const [rule, fs] of byRule) {
		const rc = summarize(fs);
		lines.push(`### ${rule} — 🔴 ${rc.error} 🟡 ${rc.warn} 🔵 ${rc.info}`);
		lines.push("");
		for (const f of fs) {
			lines.push(`- ${ICON[f.severity]} \`${f.path}\` — ${f.message}`);
		}
		lines.push("");
	}

	lines.push("## 컴포넌트 색상 제안 (디자인 의도 vs 실제 구현 vs 권장 토큰)");
	lines.push("");
	if (suggestions.length === 0) {
		lines.push("_`dist/measured.json` 없음 — 라이브(patsol.kr)/Figma 실측 후 `tokens measure`로 생성하세요._");
	} else {
		lines.push("| 컴포넌트 | 속성 | 디자인(Figma) | 구현(라이브) | 기대 토큰 | 권장 토큰 |");
		lines.push("|---|---|---|---|---|---|");
		for (const r of suggestions) {
			lines.push(
				`| ${r.component} | ${r.prop} | ${r.figma ?? "—"} | ${r.live ?? "—"} | ${r.expectedToken ?? "—"} | ${r.recommended ?? "—"} |`,
			);
		}
	}
	lines.push("");
	return lines.join("\n");
}

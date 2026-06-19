#!/usr/bin/env -S npx tsx
import { writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { normalize } from "./normalize.ts";
import { runAll, summarize } from "./validators/index.ts";
import { emitTailwind } from "./emit/tailwind.ts";
import { emitMui } from "./emit/mui.ts";
import { emitFigmaSvg } from "./emit/figma-svg.ts";
import { buildSuggestions } from "./measure/suggest.ts";
import { renderReport } from "./report/render.ts";
import { syncFigma } from "./sync/figma.ts";
import { parseNodes } from "./sync/nodes.ts";
import { diffVariables, renderDiff } from "./sync/diff.ts";
import { auditProductColors, renderAudit } from "./audit/product-colors.ts";
import { readFileSync, existsSync } from "node:fs";

const HERE = dirname(fileURLToPath(import.meta.url));
const DIST = resolve(HERE, "../dist");
const FIGMA_VARS = resolve(DIST, "figma-vars.json");

function out(name: string, content: string): string {
	mkdirSync(DIST, { recursive: true });
	const p = resolve(DIST, name);
	writeFileSync(p, content, "utf8");
	return p;
}

function doNormalize() {
	const model = normalize();
	const p = out("tokens.normalized.json", JSON.stringify({ leaves: model.leaves, byPath: model.byPath }, null, 2));
	console.log(`✓ normalize → ${p} (${model.leaves.length} leaves)`);
	return model;
}

function doLint(quiet = false) {
	const model = normalize();
	const findings = runAll(model);
	out("report.json", JSON.stringify(findings, null, 2));
	const c = summarize(findings);
	if (!quiet) {
		console.log(`✓ lint → dist/report.json`);
		console.log(`  🔴 error ${c.error} · 🟡 warn ${c.warn} · 🔵 info ${c.info}`);
		for (const f of findings.filter((x) => x.severity === "error")) {
			console.log(`  🔴 ${f.rule} ${f.path} — ${f.message}`);
		}
	}
	return { model, findings, counts: c };
}

function doReport() {
	const { model, findings } = doLint(true);
	const suggestions = buildSuggestions(model);
	const p = out("report.md", renderReport(findings, suggestions));
	console.log(`✓ report → ${p}${suggestions.length ? ` (제안 ${suggestions.length}행)` : " (measured.json 없음)"}`);
}

function doBuild(force = false) {
	const { counts } = doLint(true);
	if (counts.error > 0 && !force) {
		console.error(`✗ build 중단: lint error ${counts.error}건. 먼저 해소하세요. (dist/report.json)`);
		console.error(`  현행 SSOT 그대로 산출물이 필요하면 'build --force'.`);
		process.exit(1);
	}
	if (counts.error > 0) console.warn(`⚠ --force: lint error ${counts.error}건 무시하고 생성`);
	const tw = out("tailwind.tokens.ts", emitTailwind());
	const mui = out("mui.theme.ts", emitMui());
	console.log(`✓ build → ${tw}`);
	console.log(`✓ build → ${mui}`);
}

async function doSync() {
	const model = normalize();
	const res = await syncFigma(model);
	console.log(`sync (${res.source}): ${res.note}`);
	if (res.diff) {
		const lines = [`# Figma ↔ 코드 변수 diff`, "", res.note, ""];
		for (const d of res.diff) {
			lines.push(`- [${d.kind}] ${d.name}` + (d.code ? ` code=${d.code}` : "") + (d.figma ? ` figma=${d.figma}` : "") + (d.deltaE != null ? ` ΔE=${d.deltaE}` : ""));
		}
		const p = out("figma-diff.md", lines.join("\n"));
		console.log(`✓ sync → ${p} (${res.diff.length}건)`);
	}
}

function doNodes() {
	const targets = parseNodes();
	console.log(JSON.stringify(targets, null, 2));
	console.error(`\n파싱된 노드 ${targets.length}개. 각 노드에 get_variable_defs(fileKey, nodeId)를 호출해 ` +
		`결과를 dist/figma-vars.json (flat: {"변수명":"값"})로 저장한 뒤 'tokens figma-diff'를 실행하세요.`);
	return targets;
}

function doFigmaDiff() {
	if (!existsSync(FIGMA_VARS)) {
		console.error(`✗ ${FIGMA_VARS} 없음. 먼저 'tokens nodes'로 대상을 확인하고 get_variable_defs 결과를 저장하세요.`);
		process.exit(1);
	}
	const model = normalize();
	const vars = JSON.parse(readFileSync(FIGMA_VARS, "utf8")) as Record<string, string>;
	const res = diffVariables(model, vars);
	const note = `Figma 변수 ${Object.keys(vars).length}개 ↔ SSOT 대조 (Dev Mode MCP get_variable_defs)`;
	const p = out("figma-diff.md", renderDiff(res, note));
	const mm = res.mapped.filter((e) => e.verdict === "불일치").length;
	const absent = res.value.filter((e) => e.verdict === "코드에 없음").length;
	console.log(`✓ figma-diff → ${p} (매핑 불일치 ${mm} · 코드에 없음 ${absent})`);
}

async function main() {
	const cmd = process.argv[2] ?? "all";
	switch (cmd) {
		case "normalize":
			doNormalize();
			break;
		case "lint": {
			const { counts } = doLint();
			process.exit(counts.error > 0 ? 1 : 0);
			break;
		}
		case "report":
			doReport();
			break;
		case "build":
			doBuild(process.argv.includes("--force"));
			break;
		case "measure":
			doReport(); // measured.json 소비 → report.md
			break;
		case "sync":
			await doSync();
			break;
		case "nodes":
			doNodes();
			break;
		case "figma-diff":
			doFigmaDiff();
			break;
		case "svg":
			console.log(`✓ svg → ${out("tokens-figma.svg", emitFigmaSvg())}`);
			break;
		case "audit-product": {
			const dir = resolve(process.cwd(), process.argv[3] ?? "PatSol-Front/src");
			const { rows, fileCount } = auditProductColors(dir);
			const p = out("product-color-audit.md", renderAudit(rows, fileCount, process.argv[3] ?? "PatSol-Front/src"));
			out("product-color-audit.json", JSON.stringify(rows, null, 2));
			const c = (a: string) => rows.filter((r) => r.action === a).length;
			console.log(`✓ audit-product → ${p}`);
			console.log(`  distinct ${rows.length}종 · use-token ${c("use-token")} · merge ${c("merge")} · new ${c("new")}`);
			break;
		}
		case "all": {
			doNormalize();
			const { counts } = doLint();
			doReport();
			if (counts.error === 0) doBuild();
			else console.error(`build 생략: error ${counts.error}건`);
			break;
		}
		default:
			console.error(`알 수 없는 명령: ${cmd}\n사용: tokens <normalize|lint|report|build|measure|sync|all>`);
			process.exit(2);
	}
}

main().catch((e) => {
	console.error(e);
	process.exit(1);
});

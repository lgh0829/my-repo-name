import { readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const NODES_FILE = resolve(HERE, "../../config/figma-nodes.txt");

export interface FigmaNodeTarget {
	label: string;
	fileKey: string;
	nodeId: string; // "123:456" 형식
	raw: string;
}

/** URL에서 fileKey 추출: /design/<KEY>/ 또는 /file/<KEY>/ */
function extractFileKey(url: string): string | null {
	const m = /\/(?:design|file)\/([A-Za-z0-9]+)/.exec(url);
	return m ? m[1] : null;
}

/** URL에서 node-id 추출 후 ':' 형식으로 정규화. */
function extractNodeId(url: string): string | null {
	const m = /node-id=(\d+)[-:](\d+)/.exec(url);
	return m ? `${m[1]}:${m[2]}` : null;
}

export function parseNodes(): FigmaNodeTarget[] {
	if (!existsSync(NODES_FILE)) return [];
	const lines = readFileSync(NODES_FILE, "utf8").split(/\r?\n/);
	const out: FigmaNodeTarget[] = [];
	let auto = 0;
	for (const line of lines) {
		const t = line.trim();
		if (!t || t.startsWith("#")) continue;
		let label = "";
		let url = t;
		if (t.includes("|")) {
			const [l, ...rest] = t.split("|");
			label = l.trim();
			url = rest.join("|").trim();
		}
		const fileKey = extractFileKey(url);
		const nodeId = extractNodeId(url);
		if (!fileKey || !nodeId) continue; // node-id 없는 링크는 스킵
		out.push({ label: label || `node-${++auto}`, fileKey, nodeId, raw: url });
	}
	return out;
}

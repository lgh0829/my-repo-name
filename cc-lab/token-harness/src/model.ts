export type TokenType =
	| "color"
	| "dimension"
	| "shadow"
	| "fontFamily"
	| "fontWeight"
	| "number"
	| "other";

export type Severity = "error" | "warn" | "info";

export interface TokenLeaf {
	path: string;
	value: string | number;
	type: TokenType;
	group: string;
	refOf: string | null;
}

export interface NormalizedModel {
	leaves: TokenLeaf[];
	byPath: Record<string, string | number>;
	/** primitive/brand hex(소문자) → 토큰 경로 목록 */
	hexToPrimitive: Record<string, string[]>;
}

export interface Finding {
	rule: string;
	severity: Severity;
	path: string;
	message: string;
	data?: Record<string, unknown>;
}

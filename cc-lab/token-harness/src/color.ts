import {
	parse,
	formatHex,
	wcagContrast,
	wcagLuminance,
	differenceCiede2000,
	converter,
} from "culori";

const toOklch = converter("oklch");
const dE = differenceCiede2000();

export function isColorString(v: unknown): v is string {
	return typeof v === "string" && /^(#|rgb|rgba|hsl)/i.test(v.trim());
}

/** 색을 소문자 6자리 hex로 정규화. 파싱 실패 시 원문 소문자. */
export function normHex(v: string): string {
	const c = parse(v);
	if (!c) return v.toLowerCase();
	const h = formatHex(c);
	return (h ?? v).toLowerCase();
}

export function contrast(a: string, b: string): number {
	try {
		return wcagContrast(a, b);
	} catch {
		return NaN;
	}
}

export function luminance(a: string): number {
	try {
		return wcagLuminance(a);
	} catch {
		return NaN;
	}
}

/** oklch lightness (0~1). 파싱 실패 시 NaN. */
export function lightness(a: string): number {
	const c = toOklch(parse(a));
	return c?.l ?? NaN;
}

export function oklchOf(a: string): { l: number; c: number; h: number } | null {
	const c = toOklch(parse(a));
	if (!c) return null;
	return { l: c.l ?? NaN, c: c.c ?? NaN, h: c.h ?? NaN };
}

/** CIEDE2000 색차. */
export function deltaE(a: string, b: string): number {
	try {
		return dE(a, b);
	} catch {
		return Infinity;
	}
}

/** 두 hue 각도 간 최소 차이(deg). */
export function hueDistance(h1: number, h2: number): number {
	if (Number.isNaN(h1) || Number.isNaN(h2)) return NaN;
	const d = Math.abs(((h1 - h2 + 180) % 360) - 180);
	return d;
}

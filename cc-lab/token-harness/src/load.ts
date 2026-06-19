// SSOT 로드: designTokens-v0.2.ts 의 평가된 객체를 import (tsx 런타임).
// named export를 쓴다 — default import는 esbuild interop에서 네임스페이스로
//해석될 수 있어 .color/.typography 접근이 어긋날 수 있다.
import { designTokens } from "../designTokens-v0.2.ts";

export type RawTokens = typeof designTokens;

export function loadTokens(): RawTokens {
	return designTokens;
}

export default loadTokens;

# Figma 변수 동기화

목표: Figma의 변수와 코드 SSOT(`designTokens-v0.2.ts`)의 차이를 diff 리포트로 드러낸다. 특히 `primary` 기준(`#3361BE` 확정) 대 Figma `primary/500 #3b5ccd` 차이를 명시한다.

## 접근 경로 (가용한 것 사용)
1. **Figma Dev Mode MCP** — `get_variable_defs`(노드/선택의 변수 정의), `get_design_context`. 데스크톱 앱·선택 기반. 키 없이 동작.
2. **REST API** — `GET /v1/files/:key/variables/local`. `FIGMA_API_KEY` 환경변수 필요. 파일 전역 변수.

키/토큰은 **환경변수로만 주입**하고 코드·리포트·로그에 남기지 않는다.

## 흐름 (`src/sync/figma.ts`)
1. Figma 변수 수집 → `{ name → value }` 평탄화.
2. 정규화 토큰(`dist/tokens.normalized.json`)과 이름·값 대조.
3. diff 분류: `코드에만` / `Figma에만` / `값 불일치`.
4. `dist/figma-diff.md` 리포트 생성. 값 불일치는 hex와 ΔE를 함께 표기.

## 매핑 규칙
- Figma 컬렉션/그룹 ↔ primitive·semantic 매핑은 첫 sync 시 합의해 `config.figmaMap`에 기록한다.
- 자동 push(코드→Figma)는 기본 비활성. diff 확인 후 사람이 승인한 항목만.

## Dev Mode MCP 노드 워크플로 (권장 · 현재 경로)
REST `variables/local`은 **Enterprise 전용**이라 Pro/Starter 플랜에서 403. 대신 노드 기준 추출을 쓴다.

1. 사용자가 `config/figma-nodes.txt`에 노드 URL을 한 줄씩 붙여넣는다 (Figma: 선택 → 우클릭 → Copy link to selection. `?node-id=` 포함 필수).
2. `npx tsx src/cli.ts nodes` → URL에서 `{label, fileKey, nodeId}` 파싱 결과 출력.
3. Claude가 각 노드에 `get_variable_defs(fileKey, nodeId)` 호출 → 결과(변수명→값)를 **병합**해 `dist/figma-vars.json`(flat: `{"primary/500":"#3b5ccd", ...}`)로 저장.
4. `npx tsx src/cli.ts figma-diff` → `src/sync/diff.ts`가 변수명 마지막 세그먼트로 SSOT 토큰과 매칭, ΔE로 `값 불일치 / Figma에만 / 일치` 분류 → `dist/figma-diff.md`.

## 현재 상태
- `FIGMA_API_KEY` REST 경로: 토큰 만료/Enterprise 제약으로 비활성. 유효 토큰 + Enterprise면 `sync`로 사용 가능.
- **Dev Mode MCP 노드 경로가 기본**(토큰 불필요, `leegh@patsol.kr` 인증됨).
- sync/diff는 opt-in이며 `lint`/`build` 게이트와 무관하다.

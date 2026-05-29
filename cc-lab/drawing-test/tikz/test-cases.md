# TikZ Test Cases — Structure Diagram & Cross Section

TikZ로 특허 도면 수준의 구조도/단면도를 생성하기 위한 테스트 케이스 모음.
각 케이스는 독립 실행 가능한 `.tex` 파일로 분리한다.

---

## 공통 패키지 세트

```latex
\documentclass[border=10pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{
  shapes.geometric,   % diamond, cylinder 등
  arrows.meta,        % 화살표 스타일
  positioning,        % relative 배치 (below=of X)
  calc,               % 좌표 계산 ($P1!0.5!P2$)
  patterns,           % 해칭(hatching) — 단면도 필수
  3d,                 % 3D 좌표계
  perspective         % 원근감 있는 3D
}
```

---

## Case 1 — 레이어드 구조도 (Layered Structure Diagram)

**목표:** 박스를 수직으로 쌓아 레이어 구조를 표현. 특허 도면에서 시스템 계층 표현에 자주 사용.

**테스트 포인트:**
- 각 레이어 폭이 동일하게 정렬되는가
- 레이어 번호 (10), (20), (30) 참조번호 스타일
- 레이어 간 경계선 스타일 (solid / dashed)

```latex
% 파일: tikz/case1_layered.tex
\documentclass[border=10pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{positioning}

\tikzset{
  layer/.style = {rectangle, draw, thick, minimum width=6cm,
                  minimum height=1.2cm, align=center, inner sep=6pt},
  ref/.style   = {font=\small}
}

\begin{document}
\begin{tikzpicture}[node distance=0cm]
  \node (A) [layer] {Application Layer (30)};
  \node (B) [layer, below=of A] {Service Layer (20)};
  \node (C) [layer, below=of B] {Hardware Layer (10)};
\end{tikzpicture}
\end{document}
```

---

## Case 2 — 단면도 (Cross Section)

**목표:** 재질 경계를 해칭(hatching)으로 구분. 기계/구조 특허 도면의 핵심.

**테스트 포인트:**
- `patterns` 라이브러리로 해칭 적용 (north lines / crosshatch dots 등)
- 단면 경계선 두께
- 치수선(dimension line) 표현 가능 여부

```latex
% 파일: tikz/case2_crosssection.tex
\documentclass[border=10pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{patterns}

\begin{document}
\begin{tikzpicture}
  % 외벽 (해칭)
  \fill[pattern=north lines] (0,0) rectangle (0.5,4);
  \fill[pattern=north lines] (3.5,0) rectangle (4,4);
  % 내부 공간
  \draw[thick] (0,0) rectangle (4,4);
  \draw[thick] (0.5,0) -- (0.5,4);
  \draw[thick] (3.5,0) -- (3.5,4);
  % 내부 구조물
  \fill[pattern=crosshatch dots] (1.5,1) rectangle (2.5,3);
  \draw[thick] (1.5,1) rectangle (2.5,3);
  % 참조번호
  \node at (0.25,2) [rotate=90, font=\small] {(11)};
  \node at (3.75,2) [rotate=90, font=\small] {(12)};
  \node at (2,2)    [font=\small] {(20)};
\end{tikzpicture}
\end{document}
```

---

## Case 3 — 사시도 (Isometric / 3D Block)

**목표:** 2.5D 사시도. TikZ `3d` 라이브러리로 직육면체 표현.

**테스트 포인트:**
- x/y/z 축 벡터 설정으로 원근감 조정
- 면마다 음영(gray fill) 차등 적용
- 여러 블록 조합 시 정렬

```latex
% 파일: tikz/case3_isometric.tex
\documentclass[border=10pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{3d}

\begin{document}
\begin{tikzpicture}[
  x  = {(0.866cm, 0.5cm)},   % 30도 사시 벡터
  y  = {(0cm, 1cm)},
  z  = {(-0.866cm, 0.5cm)},
  line join=round
]
  \def\W{3} \def\H{2} \def\D{1.5}

  % 앞면
  \fill[white!90!black, draw=black, thick]
    (0,0,0) -- (\W,0,0) -- (\W,\H,0) -- (0,\H,0) -- cycle;
  % 윗면
  \fill[white!70!black, draw=black, thick]
    (0,\H,0) -- (\W,\H,0) -- (\W,\H,\D) -- (0,\H,\D) -- cycle;
  % 옆면
  \fill[white!80!black, draw=black, thick]
    (\W,0,0) -- (\W,0,\D) -- (\W,\H,\D) -- (\W,\H,0) -- cycle;

  % 참조번호
  \node at (1.5,1,0)     [font=\small] {Front (10)};
  \node at (1.5,\H,0.75) [font=\small] {Top (11)};
  \node at (\W,1,0.75)   [font=\small, rotate=-30] {Side (12)};
\end{tikzpicture}
\end{document}
```

---

## Case 4 — 조합도 (Assembly Diagram)

**목표:** 여러 부품이 결합된 구조를 분해/조합 형태로 표현.

**테스트 포인트:**
- 부품 간 연결선 및 화살표 스타일
- 점선으로 조립 방향 표시
- 참조번호 인출선 (leader line)

```latex
% 파일: tikz/case4_assembly.tex
\documentclass[border=10pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{arrows.meta, positioning}

\tikzset{
  part/.style  = {rectangle, draw, thick, minimum width=3cm,
                  minimum height=1cm, align=center},
  leader/.style = {->, >=Stealth, thin, shorten >=2pt}
}

\begin{document}
\begin{tikzpicture}[node distance=1.5cm]
  \node (top)    [part]              {Cover (30)};
  \node (mid)    [part, below=of top] {Body (20)};
  \node (bot)    [part, below=of mid] {Base (10)};

  % 조립 방향 화살표
  \draw[->, >=Stealth, thick] (top) -- (mid);
  \draw[->, >=Stealth, thick] (mid) -- (bot);

  % 인출선 + 참조번호
  \draw[leader] (top.east) -- ++(1,0) node[right] {(30)};
  \draw[leader] (mid.east) -- ++(1,0) node[right] {(20)};
  \draw[leader] (bot.east) -- ++(1,0) node[right] {(10)};
\end{tikzpicture}
\end{document}
```

---

## 렌더링 명령어

```bash
export PATH="/Library/TeX/texbin:$PATH"
cd /Users/leegh/cc-workspace/cc-lab/drawing-test

for f in tikz/case*.tex; do
  name=$(basename $f .tex)
  pdflatex -interaction=nonstopmode -output-directory=tikz $f
  pdftoppm -png tikz/${name}.pdf output/${name}
done
```

---

## 확인 기준

| 항목 | 확인 내용 |
|---|---|
| 선 굵기 | `thick` = 0.8pt, 특허 도면 기준 충족하는가 |
| 해칭 밀도 | 단면 재질 구분이 인쇄 시 명확한가 |
| 참조번호 | 번호가 도형과 겹치지 않고 인출선으로 연결되는가 |
| 3D 원근감 | 사시도 벡터 설정이 자연스러운가 |
| 글꼴 | 기본 CM 폰트 → Helvetica 변경 필요 여부 |

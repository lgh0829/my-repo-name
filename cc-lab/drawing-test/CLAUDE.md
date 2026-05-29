# drawing-test

## 실험 목표

코드 기반 도면 생성 라이브러리를 비교 실험한다.
AI(Claude)가 코드를 생성하면 오픈소스 렌더러가 PNG로 출력하는 파이프라인을 검증한다.

## 대상 도구

| 도구 | 용도 | 설치 방법 |
|---|---|---|
| Graphviz | 블록도·흐름도 | `brew install graphviz` |
| Mermaid CLI | 블록도·흐름도 | `npm install -g @mermaid-js/mermaid-cli` |
| PlantUML | 블록도·흐름도 | `brew install plantuml` |
| TikZ (TeX Live) | 사시도·결합도 | `brew install --cask mactex` |

## 폴더 구조

```
drawing-test/
├── CLAUDE.md          ← 이 문서
├── graphviz/          ← Graphviz DOT 실험
├── mermaid/           ← Mermaid 실험
├── plantuml/          ← PlantUML 실험
├── tikz/              ← TikZ LaTeX 실험
└── output/            ← 렌더링된 PNG 결과물
```

## 실험 기준

각 도구별로 동일한 도면(특허 블록도 스타일)을 그려 다음을 비교한다.

1. 코드 가독성 — AI가 생성하기 얼마나 쉬운가
2. 렌더링 품질 — 특허 도면 수준의 선명도
3. 커스터마이징 — 박스 색, 글자, 선 스타일 제어
4. 설치 난이도 — 서버 환경 Docker화 가능 여부

## 실험 방법

```bash
# Graphviz
dot -Tpng graphviz/sample.dot -o output/graphviz.png

# Mermaid
mmdc -i mermaid/sample.mmd -o output/mermaid.png

# PlantUML
plantuml -tpng plantuml/sample.puml -o ../output/

# TikZ
pdflatex tikz/sample.tex && pdftoppm -png tikz/sample.pdf output/tikz
```

오디오 파일에서 회의록을 자동 생성합니다.

인수: $ARGUMENTS
  - 형식: <오디오_파일_경로> [템플릿명]
           <메모 (선택, 2번째 줄부터 끝까지)>
  - 예시 1: /path/to/recording.m4a
  - 예시 2: /path/to/recording.m4a technical
  - 예시 3: /path/to/recording.m4a
            승봉님 의견이 핵심 — ES 구조 변경 최우선
            상훈님께 오늘 중으로 전달 필요

인수 파싱 규칙:
  - 1번째 줄: 오디오 파일 경로 (필수), 템플릿명 (선택, 공백으로 구분)
  - 2번째 줄 이후: 메모 텍스트 (선택). 전사 내용과 함께 회의록 생성에 반영됨

다음 순서로 실행하세요:

## 1단계 — 전사

아래 명령을 실행하여 오디오를 전사하세요.
vocab.json이 initial_prompt로 자동 적용되고, 임시 WAV 파일은 자동 삭제됩니다.

```bash
PATH="/opt/homebrew/bin:$PATH" python3 /Users/leegh/cc-workspace/meetings/_meeting-gen/scripts/transcribe.py "<오디오_파일_경로>"
```

전사 결과를 /tmp/meeting_transcript_latest.txt에 저장하세요:
```bash
PATH="/opt/homebrew/bin:$PATH" python3 /Users/leegh/cc-workspace/meetings/_meeting-gen/scripts/transcribe.py "<오디오_파일_경로>" > /tmp/meeting_transcript_latest.txt
```

## 2단계 — 템플릿 선택

인수에 템플릿명이 명시된 경우 해당 템플릿을 사용합니다.
명시되지 않은 경우, 전사 내용을 분석하여 아래 기준으로 자동 판단하세요:

- **technical**: API 설계, DB 구조, 파싱 로직, 배포, 버그 등 기술 구현 내용이 주를 이루는 경우
- **product**: 기능 기획, UX 정책, 요구사항 정의, 비즈니스 논의가 주를 이루는 경우
- **general**: 위 둘에 명확히 해당하지 않는 경우

판단이 애매한 경우, 사용자에게 "technical / product / general 중 어떤 템플릿을 사용할까요?"라고 물어보세요.

사용 가능한 템플릿 목록:
- /Users/leegh/cc-workspace/meetings/_meeting-gen/templates/technical.md
- /Users/leegh/cc-workspace/meetings/_meeting-gen/templates/product.md
- /Users/leegh/cc-workspace/meetings/_meeting-gen/templates/general.md

## 3단계 — 회의록 생성

선택한 템플릿을 기반으로 전사 내용을 분석하여 회의록을 작성하세요.

- {{날짜}}: 오디오 파일명 또는 현재 날짜에서 추출 (YYYY-MM-DD 형식)
- {{제목}}: 전사 내용에서 핵심 주제 추출 (한국어, 20자 이내)
- {{참석자}}: 전사에서 식별된 발화자 나열
- 전사에서 반복되거나 의미없는 구간("감사합니다" 연속, "네 네 네" 반복 등)은 생략
- 기술 용어, 고유명사는 vocab.json을 참고하여 정확하게 기재
- 메모가 있는 경우: 전사 내용보다 메모를 우선 신뢰하여 반영. 메모에서 강조된 항목은 결정 사항이나 Action Items에 우선 배치. 전사와 메모가 상충하면 메모 기준으로 작성

**노션 친화적 출력 규칙:**
- YAML frontmatter 사용 금지 — 템플릿 상단의 메타데이터 테이블 형식 유지
- Action Items는 반드시 `- [ ]` 체크박스 형태로 작성 (노션 태스크로 인식됨)
- HTML 태그 사용 금지
- 주석(`<!-- -->`)은 최종 출력에서 제거하고 실제 내용으로 채울 것

저장 경로: `/Users/leegh/cc-workspace/meetings/YYYYMMDD-<주제슬러그>.md`
파일명 예시: `260610-document-page-api.md`

## 4단계 — 정리

전사 임시 파일 삭제:
```bash
rm -f /tmp/meeting_transcript_latest.txt
```

완료 후 생성된 회의록 파일 경로를 알려주세요.

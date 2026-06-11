# Meeting Generator

회의 오디오 파일을 전사하여 구조화된 회의록을 자동 생성하는 도구 모음입니다.

---

## 디렉토리 구조

```
_meeting-gen/
  scripts/
    transcribe.py     오디오 변환 · 전사 · 후처리 · 임시파일 정리
  templates/
    technical.md      기술 회의용 템플릿
    product.md        기획·제품 회의용 템플릿
    general.md        범용 템플릿
  vocab.json          고유명사 딕셔너리 (직접 수정)
  README.md
```

---

## 사용법

Claude Code에서 슬래시 커맨드로 실행합니다.

```
/meeting <오디오_파일_경로>
```

```
/meeting <오디오_파일_경로> <템플릿명>
```

```
/meeting <오디오_파일_경로>
메모를 여기에 자유롭게 씁니다.
여러 줄도 됩니다.
```

```
/meeting <오디오_파일_경로> technical
핵심 결정사항: ES 저장 구조를 문단 배열로 변경
상훈님께 오늘 중으로 전달 필요
```

**인수 파싱 규칙**

| 위치 | 내용 | 필수 여부 |
|---|---|---|
| 1번째 줄, 첫 번째 토큰 | 오디오 파일 경로 | 필수 |
| 1번째 줄, 두 번째 토큰 | 템플릿명 (`technical` / `product` / `general`) | 선택 |
| 2번째 줄 이후 전체 | 메모 텍스트 | 선택 |

메모가 있으면 전사 내용보다 메모를 우선 신뢰하여 반영합니다.  
전사에서 불분명했던 이름·맥락을 메모로 보정할 수 있습니다.  
템플릿명을 생략하면 Claude가 전사 내용을 분석해 자동 선택하거나 선택지를 제시합니다.

---

## 워크플로우

```
[입력]
  └── m4a 음성파일 (PC · 휴대폰 녹음)
  └── 텍스트 참고파일 (선택, 샌드박스 권한 문제 시 미사용)

[처리]
  1. afconvert (macOS 내장)
       m4a → 임시 WAV (16kHz, mono, PCM)

  2. mlx-whisper (whisper-large-v3-turbo, Apple Silicon 가속)
       WAV → 전사 텍스트
       vocab.json의 people · project_terms → initial_prompt로 사전 주입
       전사 완료 후 임시 WAV 자동 삭제

  3. vocab.json 후처리
       전사 텍스트에서 오인식된 고유명사 일괄 치환

  4. Claude
       전사 텍스트 분석 → 템플릿 선택 → 주제·결정사항·액션아이템 구조화

[출력]
  └── meetings/YYMMDD-<주제슬러그>.md   (원본 오디오는 보존)
```

---

## 고유명사 딕셔너리 관리 (`vocab.json`)

```json
{
  "people": {
    "틀린전사": "올바른이름"
  },
  "project_terms": {
    "틀린용어": "올바른용어"
  },
  "hint_context": "Whisper에 전달할 배경 설명 문장"
}
```

- `people` · `project_terms` — 전사 후 자동 치환 + Whisper initial_prompt 힌트로 동시 활용
- `hint_context` — 프로젝트·도메인 배경 설명, Whisper가 전문 용어를 더 잘 인식하도록 도움
- 회의록 완성 후 오인식된 이름·용어 발견 시 추가 → 다음 회의부터 자동 반영

---

## 템플릿 추가

`templates/` 에 `.md` 파일을 추가하면 됩니다.  
파일명(확장자 제외)이 `/meeting` 커맨드의 템플릿 인수로 사용됩니다.

```
templates/legal.md  →  /meeting recording.m4a legal
```

템플릿 안에서 아래 플레이스홀더를 사용하면 Claude가 자동으로 채워 넣습니다.

| 플레이스홀더 | 치환 내용 |
|---|---|
| `{{제목}}` | 전사에서 추출한 핵심 주제 |
| `{{날짜}}` | 파일명 또는 오늘 날짜 (YYYY-MM-DD) |
| `{{참석자}}` | 전사에서 식별된 발화자 목록 |
| `{{주제}}` | 회의 주제 한 줄 요약 |

---

## 의존성

| 도구 | 설치 | 용도 |
|---|---|---|
| `afconvert` | macOS 내장 | m4a → WAV 변환 |
| `ffmpeg` | `brew install ffmpeg` | mlx-whisper 내부 디코딩 |
| `mlx-whisper` | `pip3 install mlx-whisper` | Apple Silicon 전사 |

#!/usr/bin/env python3
"""
회의 오디오 파일 전사 스크립트

Usage:
    python3 transcribe.py <audio_file_path>
    python3 transcribe.py <audio_file_path> --vocab /path/to/vocab.json

Output: 전사된 텍스트를 stdout으로 출력
Cleanup: 변환 과정에서 생성된 임시 WAV 파일 자동 삭제
"""

import sys
import os
import json
import subprocess
import re
import argparse
import tempfile

# ffmpeg PATH 보장 (brew 설치 경로)
_BREW_BIN = "/opt/homebrew/bin"
if _BREW_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _BREW_BIN + ":" + os.environ.get("PATH", "")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VOCAB = os.path.join(SCRIPT_DIR, "..", "vocab.json")  # _meeting-gen/vocab.json
MLX_MODEL = "mlx-community/whisper-large-v3-turbo"


def load_vocab(vocab_path: str) -> dict:
    path = os.path.abspath(vocab_path)
    if not os.path.exists(path):
        return {"people": {}, "project_terms": {}, "hint_context": ""}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_initial_prompt(vocab: dict) -> str:
    """vocab.json으로부터 Whisper initial_prompt 문자열 생성"""
    parts = []
    if vocab.get("hint_context"):
        parts.append(vocab["hint_context"])
    people = sorted(set(vocab.get("people", {}).values()))
    if people:
        parts.append("참석자: " + ", ".join(people))
    terms = sorted(set(vocab.get("project_terms", {}).values()))
    if terms:
        parts.append("용어: " + ", ".join(terms))
    return ". ".join(parts) if parts else None


def apply_corrections(text: str, vocab: dict) -> str:
    """전사 후 vocab의 오류 → 정답 치환 적용"""
    corrections = {}
    corrections.update(vocab.get("people", {}))
    corrections.update(vocab.get("project_terms", {}))
    for wrong, right in corrections.items():
        text = re.sub(re.escape(wrong), right, text)
    return text


def convert_to_wav(audio_path: str) -> str:
    """오디오 파일을 Whisper용 16kHz mono PCM WAV로 변환. 임시 파일 경로 반환."""
    fd, wav_path = tempfile.mkstemp(suffix=".wav", prefix="meeting_tmp_")
    os.close(fd)
    result = subprocess.run(
        ["afconvert", audio_path, wav_path, "-d", "LEI16@16000", "-f", "WAVE", "-c", "1"],
        capture_output=True
    )
    if result.returncode != 0:
        os.remove(wav_path)
        raise RuntimeError(f"afconvert 실패: {result.stderr.decode()}")
    return wav_path


def transcribe(audio_path: str, vocab_path: str = None) -> str:
    if vocab_path is None:
        vocab_path = DEFAULT_VOCAB

    vocab = load_vocab(vocab_path)
    initial_prompt = build_initial_prompt(vocab)

    print(f"[transcribe] 오디오 변환 중: {os.path.basename(audio_path)}", file=sys.stderr)
    wav_path = convert_to_wav(audio_path)

    try:
        import mlx_whisper
        print(f"[transcribe] Whisper 전사 중 (model: {MLX_MODEL.split('/')[-1]}) ...", file=sys.stderr)
        if initial_prompt:
            print(f"[transcribe] initial_prompt: {initial_prompt[:80]}...", file=sys.stderr)

        result = mlx_whisper.transcribe(
            wav_path,
            path_or_hf_repo=MLX_MODEL,
            language="ko",
            initial_prompt=initial_prompt,
            verbose=False,
        )
        text = result["text"]
    finally:
        # 임시 WAV 파일 삭제 (원본은 건드리지 않음)
        if os.path.exists(wav_path):
            os.remove(wav_path)
            print(f"[transcribe] 임시 파일 삭제 완료", file=sys.stderr)

    text = apply_corrections(text, vocab)
    return text


def main():
    parser = argparse.ArgumentParser(description="회의 오디오 전사")
    parser.add_argument("audio", help="오디오 파일 경로 (.m4a, .mp3, .wav 등)")
    parser.add_argument("--vocab", default=None, help="vocab.json 경로 (기본: meetings/vocab.json)")
    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(f"[오류] 파일을 찾을 수 없습니다: {args.audio}", file=sys.stderr)
        sys.exit(1)

    transcript = transcribe(args.audio, args.vocab)
    print(transcript)


if __name__ == "__main__":
    main()

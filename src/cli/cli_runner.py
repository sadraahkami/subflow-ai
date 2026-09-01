"""
Command-Line Interface (CLI) runner for SubFlow AI Studio.
"""

import argparse
import os
from pathlib import Path
import sys
from typing import List

from ..core.transcriber import SpeechTranscriber, TranscriptionOptions, WhisperModelSize
from ..core.sub_exporter import SubtitleExporter, SubtitleFormat
from ..core.sub_burner import SubtitleBurner, SubtitleStyleConfig, BurnStyle
from ..core.audio_tools import AudioProcessingOptions
from ..core.validator import MediaValidator


def run_cli(args: List[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="subflow",
        description="SubFlow AI - Offline AI Speech Transcription & Subtitle Studio"
    )

    parser.add_argument(
        "files",
        nargs="*",
        help="Audio or video files to transcribe"
    )
    parser.add_argument(
        "--folder", "-d",
        type=str,
        help="Process all supported media files in a directory"
    )
    parser.add_argument(
        "--model", "-m",
        choices=["tiny", "base", "small", "medium"],
        default="base",
        help="Whisper model size (default: base)"
    )
    parser.add_argument(
        "--lang", "-l",
        type=str,
        default="auto",
        help="Spoken language code (e.g. 'fa', 'en', 'ar') or 'auto'"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["srt", "vtt", "ass", "txt", "json"],
        default="srt",
        help="Output subtitle format (default: srt)"
    )
    parser.add_argument(
        "--burn", "-b",
        action="store_true",
        help="Burn / Hardcode subtitles into video output"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file or directory path"
    )
    parser.add_argument(
        "--no-vad",
        action="store_true",
        help="Disable Voice Activity Detection (VAD) filter"
    )

    parsed = parser.parse_args(args)

    target_files = []
    if parsed.files:
        target_files.extend(parsed.files)

    if parsed.folder:
        folder_p = Path(parsed.folder).resolve()
        if folder_p.exists() and folder_p.is_dir():
            for f in folder_p.iterdir():
                if f.is_file() and MediaValidator.is_supported_file(str(f)):
                    target_files.append(str(f))

    target_files = MediaValidator.filter_supported_files(target_files)

    if not target_files:
        print("[Error] No valid audio/video files provided.", file=sys.stderr)
        parser.print_help()
        return 1

    model_map = {
        "tiny": WhisperModelSize.TINY,
        "base": WhisperModelSize.BASE,
        "small": WhisperModelSize.SMALL,
        "medium": WhisperModelSize.MEDIUM,
    }
    fmt_map = {
        "srt": SubtitleFormat.SRT,
        "vtt": SubtitleFormat.VTT,
        "ass": SubtitleFormat.ASS,
        "txt": SubtitleFormat.TXT,
        "json": SubtitleFormat.JSON,
    }

    model_size = model_map.get(parsed.model, WhisperModelSize.BASE)
    export_fmt = fmt_map.get(parsed.format, SubtitleFormat.SRT)
    lang = None if parsed.lang == "auto" else parsed.lang

    options = TranscriptionOptions(
        model_size=model_size,
        language=lang,
        vad_filter=not parsed.no_vad
    )

    print("==================================================")
    print(f"[*] SubFlow AI Speech Studio (Model: {model_size.value}, Lang: {parsed.lang})")
    print(f"[*] Processing {len(target_files)} media file(s)...")
    print("==================================================")

    for idx, f_path in enumerate(target_files, start=1):
        print(f"\n[{idx}/{len(target_files)}] Transcribing: {Path(f_path).name}")

        def cli_progress(cur, total, msg):
            print(f"\r  -> [{cur}%] {msg[:50]}", end="", flush=True)

        try:
            result = SpeechTranscriber.transcribe_file(
                media_path=f_path,
                options=options,
                progress_callback=cli_progress
            )
            print()

            src_path_obj = Path(f_path)
            if parsed.output:
                out_p = Path(parsed.output)
                if out_p.is_dir() or len(target_files) > 1:
                    out_sub = out_p / f"{src_path_obj.stem}.{export_fmt.value}"
                else:
                    out_sub = out_p
            else:
                out_sub = src_path_obj.parent / f"{src_path_obj.stem}.{export_fmt.value}"

            SubtitleExporter.export_to_file(result, str(out_sub), export_fmt)
            print(f"  [+] Saved subtitle: {out_sub}")

            if parsed.burn and MediaValidator.inspect_file(f_path).is_video:
                print("  [*] Burning subtitles into video with FFmpeg...")
                out_vid = src_path_obj.parent / f"{src_path_obj.stem}_subtitled.mp4"
                SubtitleBurner.burn_subtitles_into_video(
                    video_path=f_path,
                    result=result,
                    output_video_path=str(out_vid),
                    style_config=SubtitleStyleConfig(enabled=True)
                )
                print(f"  [+] Saved subtitled video: {out_vid}")

        except Exception as e:
            print(f"\n  [Error] Failed to process {Path(f_path).name}: {e}", file=sys.stderr)

    print("\n[Done] All jobs completed successfully.")
    return 0

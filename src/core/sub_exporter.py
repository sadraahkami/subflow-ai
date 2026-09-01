"""
Multi-format subtitle exporter supporting SRT, VTT, ASS, Plain Text, and JSON.
"""

from enum import Enum
import json
from pathlib import Path
from typing import List, Optional

from .transcriber import TranscriptionResult, TranscriptionSegment
from .i18n import tr


class SubtitleFormat(Enum):
    SRT = "srt"
    VTT = "vtt"
    ASS = "ass"
    TXT = "txt"
    JSON = "json"

    @property
    def label(self) -> str:
        key = f"fmt_{self.value}"
        return tr(key)


class SubtitleExporter:

    @staticmethod
    def format_timestamp_srt(seconds: float) -> str:
        sec = max(0.0, float(seconds))
        hrs = int(sec // 3600)
        mins = int((sec % 3600) // 60)
        secs = int(sec % 60)
        millis = int(round((sec - int(sec)) * 1000))
        if millis >= 1000:
            secs += 1
            millis = 0
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def format_timestamp_vtt(seconds: float) -> str:
        sec = max(0.0, float(seconds))
        hrs = int(sec // 3600)
        mins = int((sec % 3600) // 60)
        secs = int(sec % 60)
        millis = int(round((sec - int(sec)) * 1000))
        if millis >= 1000:
            secs += 1
            millis = 0
        return f"{hrs:02d}:{mins:02d}:{secs:02d}.{millis:03d}"

    @staticmethod
    def format_timestamp_ass(seconds: float) -> str:
        sec = max(0.0, float(seconds))
        hrs = int(sec // 3600)
        mins = int((sec % 3600) // 60)
        secs = int(sec % 60)
        centis = int(round((sec - int(sec)) * 100))
        if centis >= 100:
            secs += 1
            centis = 0
        return f"{hrs:01d}:{mins:02d}:{secs:02d}.{centis:02d}"

    @classmethod
    def to_srt(cls, segments: List[TranscriptionSegment]) -> str:
        lines = []
        for idx, seg in enumerate(segments, start=1):
            if not seg.text.strip():
                continue
            start_str = cls.format_timestamp_srt(seg.start)
            end_str = cls.format_timestamp_srt(seg.end)
            lines.append(f"{idx}")
            lines.append(f"{start_str} --> {end_str}")
            lines.append(seg.text.strip())
            lines.append("")
        return "\n".join(lines)

    @classmethod
    def to_vtt(cls, segments: List[TranscriptionSegment]) -> str:
        lines = ["WEBVTT", ""]
        for idx, seg in enumerate(segments, start=1):
            if not seg.text.strip():
                continue
            start_str = cls.format_timestamp_vtt(seg.start)
            end_str = cls.format_timestamp_vtt(seg.end)
            lines.append(f"{idx}")
            lines.append(f"{start_str} --> {end_str}")
            lines.append(seg.text.strip())
            lines.append("")
        return "\n".join(lines)

    @classmethod
    def to_ass(
        cls,
        segments: List[TranscriptionSegment],
        title: str = "SubFlow AI Subtitles",
        font_name: str = "Arial",
        font_size: int = 24,
        primary_color: str = "&H00FFFFFF",  # White in BGR
        outline_color: str = "&H00000000"   # Black
    ) -> str:
        header = f"""[Script Info]
Title: {title}
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_color},&H000000FF,{outline_color},&H80000000,-1,0,0,0,100,100,0,0,1,2,1,2,10,10,25,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        event_lines = []
        for seg in segments:
            if not seg.text.strip():
                continue
            start_str = cls.format_timestamp_ass(seg.start)
            end_str = cls.format_timestamp_ass(seg.end)
            clean_text = seg.text.strip().replace("\n", "\\N")
            event_lines.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{clean_text}")

        return header + "\n".join(event_lines)

    @classmethod
    def to_txt(cls, segments: List[TranscriptionSegment]) -> str:
        return "\n\n".join(seg.text.strip() for seg in segments if seg.text.strip())

    @classmethod
    def to_json(cls, result: TranscriptionResult) -> str:
        data = {
            "model": result.model_name,
            "detected_language": result.detected_language,
            "language_probability": result.language_probability,
            "duration_seconds": result.duration_seconds,
            "full_text": result.full_text,
            "segments": [
                {
                    "id": s.id,
                    "start": s.start,
                    "end": s.end,
                    "text": s.text,
                    "words": [
                        {
                            "word": w.word,
                            "start": w.start,
                            "end": w.end,
                            "probability": w.probability
                        } for w in s.words
                    ]
                } for s in result.segments
            ]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    @classmethod
    def export_to_file(
        cls,
        result: TranscriptionResult,
        output_filepath: str,
        format_type: SubtitleFormat = SubtitleFormat.SRT
    ) -> str:
        out_path = Path(output_filepath).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if format_type == SubtitleFormat.SRT:
            content = cls.to_srt(result.segments)
        elif format_type == SubtitleFormat.VTT:
            content = cls.to_vtt(result.segments)
        elif format_type == SubtitleFormat.ASS:
            content = cls.to_ass(result.segments, title=out_path.stem)
        elif format_type == SubtitleFormat.TXT:
            content = cls.to_txt(result.segments)
        elif format_type == SubtitleFormat.JSON:
            content = cls.to_json(result)
        else:
            content = cls.to_srt(result.segments)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        return str(out_path)

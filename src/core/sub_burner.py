"""
Subtitle burning (hardcoding) engine for embedding subtitles into video using FFmpeg.
"""

from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Optional

from .validator import MediaValidator
from .sub_exporter import SubtitleExporter, SubtitleFormat
from .transcriber import TranscriptionResult
from .i18n import tr


class BurnStyle(Enum):
    TIKTOK_REELS = "burn_style_tiktok"
    CLASSIC_BOTTOM = "burn_style_classic"

    @property
    def label(self) -> str:
        return tr(self.value)


@dataclass
class SubtitleStyleConfig:
    enabled: bool = False
    style: BurnStyle = BurnStyle.TIKTOK_REELS
    font_name: str = "Arial"
    font_size: int = 24
    primary_color: str = "&H00FFFFFF"      # White BGR
    outline_color: str = "&H00000000"      # Black
    box_color: Optional[str] = "&H80000000" # Semi-transparent black box
    margin_v: int = 35


class SubtitleBurner:

    @classmethod
    def burn_subtitles_into_video(
        cls,
        video_path: str,
        result: TranscriptionResult,
        output_video_path: str,
        style_config: Optional[SubtitleStyleConfig] = None
    ) -> bool:
        if not MediaValidator.is_ffmpeg_available():
            raise RuntimeError("FFmpeg is required for burning subtitles into video.")

        config = style_config or SubtitleStyleConfig()
        src_video = str(Path(video_path).resolve())
        out_video = str(Path(output_video_path).resolve())

        Path(out_video).parent.mkdir(parents=True, exist_ok=True)

        temp_handle, temp_ass_path = tempfile.mkstemp(suffix=".ass", prefix="subflow_burn_")
        os.close(temp_handle)

        try:
            # Build tailored ASS style
            if config.style == BurnStyle.TIKTOK_REELS:
                font_size = max(20, config.font_size)
                # Vibrant Yellow / Bold White
                ass_content = SubtitleExporter.to_ass(
                    result.segments,
                    title="SubFlow AI Burn",
                    font_name=config.font_name,
                    font_size=font_size,
                    primary_color="&H0000FFFF",  # Yellow BGR
                    outline_color="&H00000000"
                )
            else:
                ass_content = SubtitleExporter.to_ass(
                    result.segments,
                    title="SubFlow AI Burn",
                    font_name=config.font_name,
                    font_size=config.font_size,
                    primary_color=config.primary_color,
                    outline_color=config.outline_color
                )

            with open(temp_ass_path, "w", encoding="utf-8") as f:
                f.write(ass_content)

            # FFmpeg filter formatting: escape backslashes and colons for Windows paths
            escaped_ass = temp_ass_path.replace("\\", "/").replace(":", "\\:")

            cmd = [
                "ffmpeg",
                "-y",
                "-i", src_video,
                "-vf", f"subtitles='{escaped_ass}'",
                "-c:a", "copy",
                "-c:v", "libx264",
                "-crf", "20",
                "-preset", "fast",
                out_video
            ]

            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg subtitle burning failed: {res.stderr}")

            return os.path.exists(out_video)

        finally:
            if os.path.exists(temp_ass_path):
                try:
                    os.remove(temp_ass_path)
                except Exception:
                    pass

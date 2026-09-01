"""
Media format validator and metadata inspector for SubFlow AI.
"""

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
from typing import List, Optional, Tuple

SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".wma", ".opus"}
SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".ts", ".flv", ".wmv", ".m4v"}
ALL_SUPPORTED_EXTENSIONS = SUPPORTED_AUDIO_EXTENSIONS | SUPPORTED_VIDEO_EXTENSIONS


@dataclass
class MediaInfo:
    filepath: str
    filename: str
    file_size_bytes: int
    is_video: bool
    duration_seconds: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None

    @property
    def formatted_size(self) -> str:
        size = float(self.file_size_bytes)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0 or unit == "GB":
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{self.file_size_bytes} B"

    @property
    def formatted_duration(self) -> str:
        if self.duration_seconds is None or self.duration_seconds <= 0:
            return "--:--"
        total_sec = int(self.duration_seconds)
        mins = total_sec // 60
        secs = total_sec % 60
        hrs = mins // 60
        mins = mins % 60
        if hrs > 0:
            return f"{hrs:02d}:{mins:02d}:{secs:02d}"
        return f"{mins:02d}:{secs:02d}"


class MediaValidator:

    @staticmethod
    def is_ffmpeg_available() -> bool:
        return shutil.which("ffmpeg") is not None

    @staticmethod
    def is_supported_file(filepath: str) -> bool:
        ext = Path(filepath).suffix.lower()
        return ext in ALL_SUPPORTED_EXTENSIONS

    @staticmethod
    def filter_supported_files(filepaths: List[str]) -> List[str]:
        valid = []
        for p in filepaths:
            if os.path.exists(p) and os.path.isfile(p):
                if MediaValidator.is_supported_file(p):
                    valid.append(str(Path(p).resolve()))
        return valid

    @staticmethod
    def inspect_file(filepath: str) -> MediaInfo:
        path_obj = Path(filepath).resolve()
        if not path_obj.exists() or not path_obj.is_file():
            raise FileNotFoundError(f"File not found: {filepath}")

        ext = path_obj.suffix.lower()
        if ext not in ALL_SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported media format: {ext}")

        size_bytes = path_obj.stat().st_size
        is_video = ext in SUPPORTED_VIDEO_EXTENSIONS

        duration: Optional[float] = None
        sample_rate: Optional[int] = None
        channels: Optional[int] = None

        if MediaValidator.is_ffmpeg_available():
            try:
                cmd = [
                    "ffprobe",
                    "-v", "error",
                    "-show_entries", "format=duration:stream=sample_rate,channels",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(path_obj)
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
                for line in lines:
                    try:
                        if "." in line and duration is None:
                            duration = float(line)
                        elif line.isdigit():
                            val = int(line)
                            if val in (1, 2, 6, 8) and channels is None:
                                channels = val
                            elif val >= 8000 and sample_rate is None:
                                sample_rate = val
                    except Exception:
                        pass
            except Exception:
                pass

        return MediaInfo(
            filepath=str(path_obj),
            filename=path_obj.name,
            file_size_bytes=size_bytes,
            is_video=is_video,
            duration_seconds=duration,
            sample_rate=sample_rate,
            channels=channels
        )

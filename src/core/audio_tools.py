"""
Audio processing, track extraction, silence trimming, and loudness normalization engine.
"""

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Optional, Tuple
import wave

from .validator import MediaValidator


@dataclass
class AudioProcessingOptions:
    sample_rate: int = 16000
    channels: int = 1
    normalize_loudness: bool = True
    noise_reduction: bool = False
    volume_boost_db: float = 0.0


class AudioProcessor:

    @classmethod
    def extract_and_prepare_audio(
        cls,
        media_path: str,
        output_wav_path: Optional[str] = None,
        options: Optional[AudioProcessingOptions] = None
    ) -> str:
        """
        Converts any audio/video media into 16kHz 16-bit mono PCM WAV for optimal Whisper transcription.
        """
        opts = options or AudioProcessingOptions()
        src_path = str(Path(media_path).resolve())

        if not os.path.exists(src_path):
            raise FileNotFoundError(f"Media file not found: {src_path}")

        if not output_wav_path:
            temp_handle, out_path = tempfile.mkstemp(suffix=".wav", prefix="subflow_audio_")
            os.close(temp_handle)
        else:
            out_path = str(Path(output_wav_path).resolve())
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)

        if MediaValidator.is_ffmpeg_available():
            filter_chain = []
            if opts.normalize_loudness:
                filter_chain.append("loudnorm=I=-16:TP=-1.5:LRA=11")
            if opts.volume_boost_db != 0.0:
                filter_chain.append(f"volume={opts.volume_boost_db}dB")

            cmd = [
                "ffmpeg",
                "-y",
                "-i", src_path,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", str(opts.sample_rate),
                "-ac", str(opts.channels),
            ]

            if filter_chain:
                cmd.extend(["-af", ",".join(filter_chain)])

            cmd.append(out_path)

            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                # Fallback to simple conversion without complex filters
                cmd_fallback = [
                    "ffmpeg", "-y", "-i", src_path,
                    "-vn", "-acodec", "pcm_s16le",
                    "-ar", str(opts.sample_rate),
                    "-ac", str(opts.channels),
                    out_path
                ]
                res_fb = subprocess.run(cmd_fallback, capture_output=True, text=True)
                if res_fb.returncode != 0:
                    raise RuntimeError(f"FFmpeg audio extraction failed: {res_fb.stderr}")
        else:
            # Fallback for raw WAV or when pydub can handle it
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(src_path)
                audio = audio.set_frame_rate(opts.sample_rate).set_channels(opts.channels).set_sample_width(2)
                if opts.normalize_loudness:
                    audio = audio.normalize()
                audio.export(out_path, format="wav")
            except Exception as e:
                # Direct copy if it's already a wav file
                if src_path.lower().endswith(".wav"):
                    shutil.copy2(src_path, out_path)
                else:
                    raise RuntimeError(
                        f"FFmpeg is recommended for extracting audio from {Path(src_path).suffix} files. Error: {e}"
                    )

        return out_path

    @staticmethod
    def get_wav_duration_seconds(wav_path: str) -> float:
        try:
            with wave.open(wav_path, "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                if rate > 0:
                    return frames / float(rate)
        except Exception:
            pass
        return 0.0

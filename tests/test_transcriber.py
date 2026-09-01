"""
Unit tests for Transcriber Data Structures and Pipeline in SubFlow AI.
"""

import os
import tempfile
import unittest
import wave
import numpy as np

from src.core.transcriber import (
    SpeechTranscriber, TranscriptionOptions, TranscriptionSegment,
    TranscriptionResult, WhisperModelSize
)
from src.core.sub_exporter import SubtitleExporter, SubtitleFormat


class TestTranscriber(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="subflow_test_trans_")
        self.wav_path = os.path.join(self.temp_dir, "speech_sample.wav")
        sample_rate = 16000
        duration = 2.0
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio_data = (np.sin(2 * np.pi * 300 * t) * 32767).astype(np.int16)

        with wave.open(self.wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_transcribe_pipeline_execution(self):
        opts = TranscriptionOptions(
            model_size=WhisperModelSize.TINY,
            language="en"
        )
        result = SpeechTranscriber.transcribe_file(
            media_path=self.wav_path,
            options=opts
        )
        self.assertIsInstance(result, TranscriptionResult)
        self.assertGreater(len(result.segments), 0)
        self.assertTrue(len(result.full_text) > 0)
        self.assertGreater(result.duration_seconds, 0)

    def test_export_integration(self):
        opts = TranscriptionOptions(model_size=WhisperModelSize.BASE)
        result = SpeechTranscriber.transcribe_file(self.wav_path, options=opts)
        out_srt = os.path.join(self.temp_dir, "test.srt")
        saved = SubtitleExporter.export_to_file(result, out_srt, SubtitleFormat.SRT)
        self.assertTrue(os.path.exists(saved))
        with open(saved, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("-->", content)


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for Audio Tools & Preparation in SubFlow AI.
"""

import os
from pathlib import Path
import tempfile
import unittest
import wave
import numpy as np

from src.core.audio_tools import AudioProcessor, AudioProcessingOptions


class TestAudioTools(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="subflow_test_audio_")
        # Create a dummy 1-second 16kHz sine wave audio file
        self.wav_path = os.path.join(self.temp_dir, "test_sine.wav")
        sample_rate = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio_data = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)

        with wave.open(self.wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_wav_duration(self):
        dur = AudioProcessor.get_wav_duration_seconds(self.wav_path)
        self.assertAlmostEqual(dur, 1.0, places=1)

    def test_extract_and_prepare_audio(self):
        out_wav = AudioProcessor.extract_and_prepare_audio(self.wav_path)
        self.assertTrue(os.path.exists(out_wav))
        self.assertGreater(os.path.getsize(out_wav), 0)
        dur = AudioProcessor.get_wav_duration_seconds(out_wav)
        self.assertAlmostEqual(dur, 1.0, places=1)
        if os.path.exists(out_wav):
            os.remove(out_wav)


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for Media Format Validator and Inspector in SubFlow AI.
"""

import os
import tempfile
import unittest
from src.core.validator import MediaValidator, SUPPORTED_AUDIO_EXTENSIONS, SUPPORTED_VIDEO_EXTENSIONS


class TestMediaValidator(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="subflow_test_val_")
        self.dummy_audio = os.path.join(self.temp_dir, "sample.mp3")
        with open(self.dummy_audio, "wb") as f:
            f.write(b"ID3" + b"\x00" * 1024)

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_extension_detection(self):
        self.assertTrue(MediaValidator.is_supported_file("video.mp4"))
        self.assertTrue(MediaValidator.is_supported_file("song.flac"))
        self.assertTrue(MediaValidator.is_supported_file("voice.wav"))
        self.assertFalse(MediaValidator.is_supported_file("document.pdf"))
        self.assertFalse(MediaValidator.is_supported_file("archive.zip"))

    def test_inspect_file(self):
        info = MediaValidator.inspect_file(self.dummy_audio)
        self.assertEqual(info.filename, "sample.mp3")
        self.assertFalse(info.is_video)
        self.assertGreater(info.file_size_bytes, 0)
        self.assertIn("KB", info.formatted_size)


if __name__ == "__main__":
    unittest.main()

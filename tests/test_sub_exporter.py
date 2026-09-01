"""
Unit tests for SubFlow AI Subtitle Exporter (SRT, VTT, ASS, JSON, TXT).
"""

import json
import unittest
from src.core.transcriber import TranscriptionSegment, TranscriptionResult, WordTimestamp
from src.core.sub_exporter import SubtitleExporter, SubtitleFormat


class TestSubtitleExporter(unittest.TestCase):

    def setUp(self):
        self.segments = [
            TranscriptionSegment(
                id=1,
                start=1.234,
                end=4.567,
                text="سلام این یک آزمایش است.",
                words=[
                    WordTimestamp("سلام", 1.234, 1.8),
                    WordTimestamp("این", 1.8, 2.3),
                    WordTimestamp("یک", 2.3, 2.9),
                    WordTimestamp("آزمایش", 2.9, 3.8),
                    WordTimestamp("است", 3.8, 4.567),
                ]
            ),
            TranscriptionSegment(
                id=2,
                start=5.0,
                end=8.125,
                text="Welcome to SubFlow AI Studio.",
                words=[
                    WordTimestamp("Welcome", 5.0, 5.8),
                    WordTimestamp("to", 5.8, 6.2),
                    WordTimestamp("SubFlow", 6.2, 7.0),
                    WordTimestamp("AI", 7.0, 7.5),
                    WordTimestamp("Studio", 7.5, 8.125),
                ]
            )
        ]
        self.result = TranscriptionResult(
            segments=self.segments,
            detected_language="fa",
            language_probability=0.98,
            duration_seconds=8.5,
            model_name="base"
        )

    def test_srt_formatting(self):
        srt = SubtitleExporter.to_srt(self.segments)
        self.assertIn("1", srt)
        self.assertIn("00:00:01,234 --> 00:00:04,567", srt)
        self.assertIn("سلام این یک آزمایش است.", srt)
        self.assertIn("2", srt)
        self.assertIn("00:00:05,000 --> 00:00:08,125", srt)
        self.assertIn("Welcome to SubFlow AI Studio.", srt)

    def test_vtt_formatting(self):
        vtt = SubtitleExporter.to_vtt(self.segments)
        self.assertTrue(vtt.startswith("WEBVTT"))
        self.assertIn("00:00:01.234 --> 00:00:04.567", vtt)

    def test_ass_formatting(self):
        ass = SubtitleExporter.to_ass(self.segments)
        self.assertIn("[Script Info]", ass)
        self.assertIn("[V4+ Styles]", ass)
        self.assertIn("[Events]", ass)
        self.assertIn("Dialogue: 0,0:00:01.23,0:00:04.57,Default,,0,0,0,,سلام این یک آزمایش است.", ass)

    def test_json_formatting(self):
        json_str = SubtitleExporter.to_json(self.result)
        parsed = json.loads(json_str)
        self.assertEqual(parsed["model"], "base")
        self.assertEqual(parsed["detected_language"], "fa")
        self.assertEqual(len(parsed["segments"]), 2)
        self.assertEqual(parsed["segments"][0]["words"][0]["word"], "سلام")

    def test_txt_formatting(self):
        txt = SubtitleExporter.to_txt(self.segments)
        self.assertIn("سلام این یک آزمایش است.", txt)
        self.assertIn("Welcome to SubFlow AI Studio.", txt)


if __name__ == "__main__":
    unittest.main()

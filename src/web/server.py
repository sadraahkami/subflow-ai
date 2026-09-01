"""
Lightweight REST Web Server and Static Asset Handler for SubFlow AI.
"""

import base64
import json
import mimetypes
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional

from ..core.transcriber import (
    SpeechTranscriber, TranscriptionOptions, WhisperModelSize
)
from ..core.sub_exporter import SubtitleExporter, SubtitleFormat
from ..core.validator import MediaValidator

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    STATIC_DIR = Path(sys._MEIPASS) / "src" / "web" / "static"
else:
    STATIC_DIR = Path(__file__).resolve().parent / "static"


class SubFlowHttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        url_path = self.path.split("?")[0]

        if url_path == "/" or url_path == "":
            self._serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return

        if url_path == "/api/health":
            self._send_json({"status": "ok", "app": "SubFlow AI Studio", "version": "1.0.0"})
            return

        clean_path = url_path.lstrip("/")
        target_static = STATIC_DIR / clean_path
        if target_static.exists() and target_static.is_file():
            mime, _ = mimetypes.guess_type(str(target_static))
            if clean_path.endswith(".js"):
                mime = "application/javascript"
            elif clean_path.endswith(".css"):
                mime = "text/css"
            self._serve_file(target_static, mime or "application/octet-stream")
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/api/transcribe":
            self._handle_api_transcribe()
            return

        self.send_error(404, "Endpoint Not Found")

    def _serve_file(self, file_path: Path, content_type: str):
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def _handle_api_transcribe(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            self._send_json({"error": "Empty request payload"}, 400)
            return

        raw_data = self.rfile.read(content_length)
        try:
            payload = json.loads(raw_data.decode("utf-8"))
        except Exception as e:
            self._send_json({"error": f"Invalid JSON: {e}"}, 400)
            return

        file_b64 = payload.get("fileData", "")
        file_name = payload.get("fileName", "audio.mp3")
        model_name = payload.get("model", "base")
        lang = payload.get("language", "auto")
        fmt = payload.get("format", "srt")
        vad = payload.get("vad", True)

        if not file_b64:
            self._send_json({"error": "No file data provided"}, 400)
            return

        if "," in file_b64:
            file_b64 = file_b64.split(",", 1)[1]

        temp_dir = tempfile.mkdtemp(prefix="subflow_web_")
        try:
            file_bytes = base64.b64decode(file_b64)
            ext = Path(file_name).suffix or ".mp3"
            src_media_path = os.path.join(temp_dir, f"input_media{ext}")

            with open(src_media_path, "wb") as f:
                f.write(file_bytes)

            model_map = {
                "tiny": WhisperModelSize.TINY,
                "base": WhisperModelSize.BASE,
                "small": WhisperModelSize.SMALL,
                "medium": WhisperModelSize.MEDIUM,
            }

            options = TranscriptionOptions(
                model_size=model_map.get(model_name, WhisperModelSize.BASE),
                language=None if lang == "auto" else lang,
                vad_filter=bool(vad)
            )

            result = SpeechTranscriber.transcribe_file(src_media_path, options=options)

            # Export formatting
            srt_text = SubtitleExporter.to_srt(result.segments)
            vtt_text = SubtitleExporter.to_vtt(result.segments)
            ass_text = SubtitleExporter.to_ass(result.segments)
            txt_text = SubtitleExporter.to_txt(result.segments)
            json_text = SubtitleExporter.to_json(result)

            self._send_json({
                "success": True,
                "model": result.model_name,
                "detectedLanguage": result.detected_language,
                "duration": result.duration_seconds,
                "fullText": result.full_text,
                "subtitles": {
                    "srt": srt_text,
                    "vtt": vtt_text,
                    "ass": ass_text,
                    "txt": txt_text,
                    "json": json_text
                }
            })

        except Exception as e:
            self._send_json({"error": str(e)}, 500)
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _send_json(self, data: dict, status_code: int = 200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def start_web_server(host: str = "127.0.0.1", port: int = 8080, open_browser: bool = True):
    server_address = (host, port)
    try:
        httpd = HTTPServer(server_address, SubFlowHttpHandler)
    except OSError:
        port = 8081
        server_address = (host, port)
        httpd = HTTPServer(server_address, SubFlowHttpHandler)

    url = f"http://{host}:{port}"
    print("==================================================")
    print(f"[*] SubFlow AI Web Studio running at: {url}")
    print(f"[*] Press Ctrl+C in terminal to stop server.")
    print("==================================================")

    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping SubFlow web server...")
        httpd.server_close()

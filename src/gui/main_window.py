"""
Main Desktop Application Window for SubFlow AI Studio with PyQt6.
"""

import os
from pathlib import Path
import subprocess
from typing import List, Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QSize
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QComboBox, QCheckBox, QProgressBar, QTextEdit,
    QGroupBox, QListWidgetItem, QSpinBox, QSplitter
)

from ..core.i18n import tr, set_current_language, get_current_language
from ..core.validator import MediaValidator, MediaInfo, ALL_SUPPORTED_EXTENSIONS
from ..core.audio_tools import AudioProcessingOptions
from ..core.transcriber import (
    SpeechTranscriber, TranscriptionOptions, TranscriptionResult,
    WhisperModelSize
)
from ..core.sub_exporter import SubtitleExporter, SubtitleFormat
from ..core.sub_burner import SubtitleBurner, SubtitleStyleConfig, BurnStyle
from .icons import IconProvider
from .styles import DARK_THEME
from .widgets import MediaCardWidget, DropZoneListWidget


class TranscriptionWorker(QObject):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(bool, object, str)

    def __init__(
        self,
        media_path: str,
        trans_options: TranscriptionOptions,
        audio_options: AudioProcessingOptions,
        burn_config: SubtitleStyleConfig,
        export_format: SubtitleFormat,
        output_dir: str
    ):
        super().__init__()
        self.media_path = media_path
        self.trans_options = trans_options
        self.audio_options = audio_options
        self.burn_config = burn_config
        self.export_format = export_format
        self.output_dir = output_dir
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            def on_progress(cur, total, msg):
                self.progress.emit(cur, total, msg)

            result = SpeechTranscriber.transcribe_file(
                media_path=self.media_path,
                options=self.trans_options,
                progress_callback=on_progress,
                is_cancelled=lambda: self._is_cancelled
            )

            # Export Subtitle File
            src_stem = Path(self.media_path).stem
            sub_filename = f"{src_stem}.{self.export_format.value}"
            sub_out_path = os.path.join(self.output_dir, sub_filename)
            SubtitleExporter.export_to_file(result, sub_out_path, self.export_format)

            # Optional Subtitle Burning
            if self.burn_config.enabled and MediaValidator.inspect_file(self.media_path).is_video:
                on_progress(95, 100, tr("burning_subtitles"))
                burnt_video_path = os.path.join(self.output_dir, f"{src_stem}_subtitled.mp4")
                SubtitleBurner.burn_subtitles_into_video(
                    video_path=self.media_path,
                    result=result,
                    output_video_path=burnt_video_path,
                    style_config=self.burn_config
                )

            self.finished.emit(True, result, sub_out_path)

        except Exception as e:
            self.finished.emit(False, None, str(e))


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.media_files: List[MediaInfo] = []
        self.thread: Optional[QThread] = None
        self.worker: Optional[TranscriptionWorker] = None
        self.latest_result: Optional[TranscriptionResult] = None
        self.latest_output_path: Optional[str] = None

        self._init_window()
        self._build_ui()
        self._retranslate_ui()
        self._update_ui_state()

    def _init_window(self):
        self.resize(1180, 800)
        self.setMinimumSize(920, 620)
        self.setStyleSheet(DARK_THEME)

    def _build_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Top Action Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.btn_add_files = QPushButton()
        self.btn_add_files.setIcon(IconProvider.get_icon("add_files", "#FFFFFF", 20))
        self.btn_add_files.setIconSize(QSize(18, 18))
        self.btn_add_files.clicked.connect(self._on_add_files)

        self.btn_clear_all = QPushButton()
        self.btn_clear_all.setIcon(IconProvider.get_icon("clear", "#FFFFFF", 20))
        self.btn_clear_all.setIconSize(QSize(18, 18))
        self.btn_clear_all.setObjectName("dangerBtn")
        self.btn_clear_all.clicked.connect(self._on_clear_all)

        self.btn_lang = QPushButton()
        self.btn_lang.setObjectName("langBtn")
        self.btn_lang.clicked.connect(self._toggle_language)

        top_bar.addWidget(self.btn_add_files)
        top_bar.addWidget(self.btn_clear_all)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_lang)
        main_layout.addLayout(top_bar)

        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Left: File List & Drop Zone
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self.list_widget = DropZoneListWidget()
        self.list_widget.files_dropped.connect(self._add_media_paths)
        left_layout.addWidget(self.list_widget)

        self.lbl_file_count = QLabel()
        self.lbl_file_count.setStyleSheet("color: #94A3B8; font-size: 12px;")
        left_layout.addWidget(self.lbl_file_count)

        splitter.addWidget(left_widget)

        # Center / Right: Settings & Preview Panel
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Settings Group
        self.grp_settings = QGroupBox()
        settings_grid = QVBoxLayout(self.grp_settings)
        settings_grid.setSpacing(8)

        # Model row
        row_model = QHBoxLayout()
        self.lbl_model = QLabel()
        self.lbl_model.setStyleSheet("font-weight: bold; color: #E2E8F0;")
        self.combo_model = QComboBox()
        self.combo_model.addItem("Base (Recommended)", WhisperModelSize.BASE)
        self.combo_model.addItem("Tiny (Fastest)", WhisperModelSize.TINY)
        self.combo_model.addItem("Small (High Accuracy)", WhisperModelSize.SMALL)
        self.combo_model.addItem("Medium (Max Precision)", WhisperModelSize.MEDIUM)
        row_model.addWidget(self.lbl_model)
        row_model.addWidget(self.combo_model, stretch=1)
        settings_grid.addLayout(row_model)

        # Language row
        row_lang = QHBoxLayout()
        self.lbl_lang = QLabel()
        self.lbl_lang.setStyleSheet("font-weight: bold; color: #E2E8F0;")
        self.combo_lang = QComboBox()
        self.combo_lang.addItem("Auto Detect", "auto")
        self.combo_lang.addItem("Persian (فارسی)", "fa")
        self.combo_lang.addItem("English", "en")
        self.combo_lang.addItem("Arabic (العربية)", "ar")
        self.combo_lang.addItem("French", "fr")
        self.combo_lang.addItem("German", "de")
        self.combo_lang.addItem("Spanish", "es")
        self.combo_lang.addItem("Turkish", "tr")
        row_lang.addWidget(self.lbl_lang)
        row_lang.addWidget(self.combo_lang, stretch=1)
        settings_grid.addLayout(row_lang)

        # Output Format row
        row_fmt = QHBoxLayout()
        self.lbl_fmt = QLabel()
        self.lbl_fmt.setStyleSheet("font-weight: bold; color: #E2E8F0;")
        self.combo_fmt = QComboBox()
        self.combo_fmt.addItem("SRT (SubRip Standard)", SubtitleFormat.SRT)
        self.combo_fmt.addItem("VTT (WebVTT HTML5)", SubtitleFormat.VTT)
        self.combo_fmt.addItem("ASS (Advanced Styling)", SubtitleFormat.ASS)
        self.combo_fmt.addItem("TXT (Plain Text)", SubtitleFormat.TXT)
        self.combo_fmt.addItem("JSON (Full Timestamps)", SubtitleFormat.JSON)
        row_fmt.addWidget(self.lbl_fmt)
        row_fmt.addWidget(self.combo_fmt, stretch=1)
        settings_grid.addLayout(row_fmt)

        # Audio Enhancements
        self.chk_vad = QCheckBox()
        self.chk_vad.setChecked(True)
        settings_grid.addWidget(self.chk_vad)

        self.chk_norm = QCheckBox()
        self.chk_norm.setChecked(True)
        settings_grid.addWidget(self.chk_norm)

        # Subtitle Burning Checkbox
        self.chk_burn = QCheckBox()
        self.chk_burn.setChecked(False)
        settings_grid.addWidget(self.chk_burn)

        right_layout.addWidget(self.grp_settings)

        # Transcript Preview Box
        self.lbl_preview_title = QLabel()
        self.lbl_preview_title.setStyleSheet("font-weight: bold; color: #38BDF8;")
        right_layout.addWidget(self.lbl_preview_title)

        self.txt_preview = QTextEdit()
        self.txt_preview.setReadOnly(False)
        self.txt_preview.setPlaceholderText("Transcription preview will appear here...")
        right_layout.addWidget(self.txt_preview, stretch=1)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)
        main_layout.addWidget(splitter, stretch=1)

        # Bottom Progress & Action Bar
        bottom_box = QVBoxLayout()
        bottom_box.setSpacing(6)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        bottom_box.addWidget(self.progress_bar)

        self.lbl_status = QLabel()
        self.lbl_status.setStyleSheet("color: #38BDF8; font-weight: bold;")
        bottom_box.addWidget(self.lbl_status)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.btn_transcribe = QPushButton()
        self.btn_transcribe.setFixedHeight(44)
        self.btn_transcribe.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10B981, stop:1 #059669);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34D399, stop:1 #10B981);
            }
        """)
        self.btn_transcribe.clicked.connect(self._on_start_transcribe)

        self.btn_open_folder = QPushButton()
        self.btn_open_folder.setObjectName("secondaryBtn")
        self.btn_open_folder.setFixedHeight(44)
        self.btn_open_folder.clicked.connect(self._on_open_folder)

        action_row.addWidget(self.btn_transcribe, stretch=2)
        action_row.addWidget(self.btn_open_folder, stretch=1)
        bottom_box.addLayout(action_row)

        main_layout.addLayout(bottom_box)

    def _retranslate_ui(self):
        is_rtl = get_current_language() == "fa"
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if is_rtl else Qt.LayoutDirection.LeftToRight)

        self.setWindowTitle(tr("app_title"))
        self.btn_add_files.setText(tr("add_files"))
        self.btn_clear_all.setText(tr("clear_all"))
        self.btn_lang.setText(tr("lang_toggle_btn"))

        self.grp_settings.setTitle(tr("pdf_settings" if False else "app_title"))
        self.lbl_model.setText(tr("model_label"))
        self.lbl_lang.setText(tr("language_label"))
        self.lbl_fmt.setText(tr("format_label"))

        self.chk_vad.setText(tr("vad_filter"))
        self.chk_norm.setText(tr("audio_normalize"))
        self.chk_burn.setText(tr("burn_enable"))

        self.lbl_preview_title.setText(tr("preview_tab"))
        self.btn_transcribe.setText(tr("start_transcribe_btn"))
        self.btn_open_folder.setText(tr("open_folder"))

        self._update_file_count_label()

    def _update_file_count_label(self):
        count = len(self.media_files)
        if count == 0:
            self.lbl_file_count.setText(tr("no_files_selected"))
        else:
            total_bytes = sum(m.file_size_bytes for m in self.media_files)
            fmt_size = MediaInfo("", "", total_bytes, False).formatted_size
            self.lbl_file_count.setText(tr("files_selected_count", count=count, size=fmt_size))

    def _update_ui_state(self):
        has_files = len(self.media_files) > 0
        self.btn_clear_all.setEnabled(has_files)
        self.btn_transcribe.setEnabled(has_files)
        self.btn_open_folder.setEnabled(self.latest_output_path is not None)

    def _toggle_language(self):
        new_lang = "en" if get_current_language() == "fa" else "fa"
        set_current_language(new_lang)
        self._retranslate_ui()

    def _on_add_files(self):
        ext_filter = "Media Files (*.mp3 *.wav *.flac *.m4a *.mp4 *.mkv *.mov *.webm *.avi);;All Files (*.*)"
        files, _ = QFileDialog.getOpenFileNames(self, tr("add_files"), "", ext_filter)
        if files:
            self._add_media_paths(files)

    def _add_media_paths(self, paths: List[str]):
        for p in paths:
            try:
                info = MediaValidator.inspect_file(p)
                if not any(m.filepath == info.filepath for m in self.media_files):
                    self.media_files.append(info)
                    item = QListWidgetItem(self.list_widget)
                    card = MediaCardWidget(info)
                    card.delete_requested.connect(self._remove_file)
                    item.setSizeHint(card.sizeHint())
                    self.list_widget.addItem(item)
                    self.list_widget.setItemWidget(item, card)
            except Exception as e:
                QMessageBox.warning(self, tr("error_title"), f"Error loading {Path(p).name}: {e}")

        self._update_file_count_label()
        self._update_ui_state()

    def _remove_file(self, filepath: str):
        self.media_files = [m for m in self.media_files if m.filepath != filepath]
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            card = self.list_widget.itemWidget(item)
            if card and card.media_info.filepath == filepath:
                self.list_widget.takeItem(i)
                break
        self._update_file_count_label()
        self._update_ui_state()

    def _on_clear_all(self):
        self.media_files.clear()
        self.list_widget.clear()
        self.txt_preview.clear()
        self._update_file_count_label()
        self._update_ui_state()

    def _on_start_transcribe(self):
        if not self.media_files:
            QMessageBox.warning(self, tr("error_title"), tr("error_empty"))
            return

        target_media = self.media_files[0].filepath
        output_dir = str(Path(target_media).parent)

        trans_opts = TranscriptionOptions(
            model_size=self.combo_model.currentData() or WhisperModelSize.BASE,
            language=self.combo_lang.currentData(),
            vad_filter=self.chk_vad.isChecked()
        )

        audio_opts = AudioProcessingOptions(
            normalize_loudness=self.chk_norm.isChecked()
        )

        burn_cfg = SubtitleStyleConfig(
            enabled=self.chk_burn.isChecked()
        )

        export_fmt = self.combo_fmt.currentData() or SubtitleFormat.SRT

        self.btn_transcribe.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText(tr("ready"))

        self.thread = QThread()
        self.worker = TranscriptionWorker(
            media_path=target_media,
            trans_options=trans_opts,
            audio_options=audio_opts,
            burn_config=burn_cfg,
            export_format=export_fmt,
            output_dir=output_dir
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self._on_worker_progress)
        self.worker.finished.connect(self._on_worker_finished)

        self.thread.start()

    def _on_worker_progress(self, cur: int, total: int, msg: str):
        self.progress_bar.setValue(cur)
        self.lbl_status.setText(msg)

    def _on_worker_finished(self, success: bool, result: Optional[TranscriptionResult], out_path: str):
        if self.thread:
            self.thread.quit()
            self.thread.wait()

        self.btn_transcribe.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success and result:
            self.latest_result = result
            self.latest_output_path = out_path
            self.lbl_status.setText(tr("completed_success"))

            # Fill preview text
            preview_lines = []
            for seg in result.segments:
                start_s = SubtitleExporter.format_timestamp_srt(seg.start)
                end_s = SubtitleExporter.format_timestamp_srt(seg.end)
                preview_lines.append(f"[{start_s} --> {end_s}]\n{seg.text}\n")
            self.txt_preview.setPlainText("\n".join(preview_lines))

            QMessageBox.information(
                self,
                tr("success_title"),
                f"{tr('completed_success')}\n\nSaved to: {out_path}"
            )
        else:
            self.lbl_status.setText(tr("error_title"))
            QMessageBox.critical(self, tr("error_title"), f"Transcription Error:\n{out_path}")

        self._update_ui_state()

    def _on_open_folder(self):
        if self.latest_output_path and os.path.exists(self.latest_output_path):
            folder = str(Path(self.latest_output_path).parent)
            if os.name == "nt":
                subprocess.run(["explorer", folder])
            else:
                subprocess.run(["xdg-open", folder])

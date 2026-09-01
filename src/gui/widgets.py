"""
Custom Qt Widgets for SubFlow AI Desktop Interface.
"""

from pathlib import Path
from typing import Callable, Optional

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QFrame
)
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from ..core.validator import MediaInfo, MediaValidator
from .icons import IconProvider


class MediaCardWidget(QFrame):
    delete_requested = pyqtSignal(str)

    def __init__(self, media_info: MediaInfo, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.media_info = media_info

        self.setStyleSheet("""
            MediaCardWidget {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 10px;
                margin: 2px 0;
            }
            MediaCardWidget:hover {
                border-color: #38BDF8;
                background-color: #243247;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        # Type Icon (Mic / Video)
        icon_lbl = QLabel()
        icon_name = "video" if media_info.is_video else "mic"
        icon_lbl.setPixmap(IconProvider.get_icon(icon_name, "#38BDF8", 22).pixmap(22, 22))
        layout.addWidget(icon_lbl)

        # File Details Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_lbl = QLabel(media_info.filename)
        name_lbl.setStyleSheet("font-weight: bold; color: #F8FAFC; font-size: 13px;")
        info_layout.addWidget(name_lbl)

        meta_text = f"{media_info.formatted_size} | {media_info.formatted_duration}"
        meta_lbl = QLabel(meta_text)
        meta_lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
        info_layout.addWidget(meta_lbl)

        layout.addLayout(info_layout, stretch=1)

        # Delete Button
        del_btn = QPushButton()
        del_btn.setIcon(IconProvider.get_icon("trash", "#EF4444", 16))
        del_btn.setIconSize(QSize(16, 16))
        del_btn.setFixedSize(28, 28)
        del_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7F1D1D;
            }
        """)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.media_info.filepath))
        layout.addWidget(del_btn)


class DropZoneListWidget(QListWidget):
    files_dropped = pyqtSignal(list)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            paths = []
            for url in event.mimeData().urls():
                lp = url.toLocalFile()
                if lp:
                    paths.append(lp)
            valid_files = MediaValidator.filter_supported_files(paths)
            if valid_files:
                self.files_dropped.emit(valid_files)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

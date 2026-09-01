"""
Modern Neon Dark Theme stylesheet for SubFlow AI.
"""

DARK_THEME = """
QMainWindow {
    background-color: #0F172A;
    color: #F8FAFC;
}

QWidget {
    background-color: transparent;
    color: #F8FAFC;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Vazirmatn', Tahoma, sans-serif;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 18px;
    padding-top: 14px;
    padding-bottom: 10px;
    padding-left: 10px;
    padding-right: 10px;
    font-weight: bold;
    color: #38BDF8;
    background-color: #1E293B;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    background-color: #0F172A;
    border-radius: 4px;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 9px 18px;
    font-weight: bold;
    min-height: 20px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #60A5FA, stop:1 #3B82F6);
}

QPushButton:pressed {
    background-color: #1D4ED8;
}

QPushButton:disabled {
    background-color: #334155;
    color: #64748B;
}

QPushButton#secondaryBtn {
    background-color: #334155;
    color: #F1F5F9;
    border: 1px solid #475569;
}

QPushButton#secondaryBtn:hover {
    background-color: #475569;
}

QPushButton#dangerBtn {
    background-color: #DC2626;
    color: #FFFFFF;
}

QPushButton#dangerBtn:hover {
    background-color: #EF4444;
}

QPushButton#langBtn {
    background-color: #1E293B;
    color: #38BDF8;
    border: 1px solid #38BDF8;
    padding: 6px 12px;
}

QComboBox {
    background-color: #1E293B;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 6px 10px;
    color: #F8FAFC;
    min-height: 22px;
}

QComboBox:hover {
    border-color: #38BDF8;
}

QComboBox QAbstractItemView {
    background-color: #1E293B;
    border: 1px solid #475569;
    selection-background-color: #2563EB;
    color: #F8FAFC;
    padding: 4px;
}

QCheckBox {
    spacing: 8px;
    color: #E2E8F0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #1E293B;
}

QCheckBox::indicator:checked {
    background-color: #2563EB;
    border-color: #38BDF8;
}

QProgressBar {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 6px;
    height: 14px;
    text-align: center;
    color: #FFFFFF;
    font-size: 11px;
    font-weight: bold;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #06B6D4, stop:1 #3B82F6);
    border-radius: 5px;
}

QListWidget {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px;
}

QTextEdit {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #F1F5F9;
    padding: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}

QScrollBar:vertical {
    border: none;
    background: #0F172A;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}
"""

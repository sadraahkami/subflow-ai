"""
Internationalization (i18n) module supporting Persian (RTL) and English (LTR).
"""

from typing import Dict, Optional

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "app_title": {
        "fa": "استودیوی هوشمند رونویسی گفتار و زیرنویس SubFlow AI",
        "en": "SubFlow AI - Smart Speech & Subtitle Studio"
    },
    "add_files": {
        "fa": "افزودن فایل‌های صوتی/تصویری...",
        "en": "Add Media Files..."
    },
    "clear_all": {
        "fa": "پاک‌سازی لیست",
        "en": "Clear List"
    },
    "no_files_selected": {
        "fa": "هیچ فایلی انتخاب نشده است (فایل‌ها را به این قسمت بکشید و رها کنید)",
        "en": "No files selected (Drag & drop media files here)"
    },
    "files_selected_count": {
        "fa": "{count} فایل انتخاب شده ({size})",
        "en": "{count} files selected ({size})"
    },
    # Model Selection
    "model_label": {
        "fa": "مدل هوش مصنوعی (Whisper Model):",
        "en": "AI Whisper Model:"
    },
    "model_tiny": {
        "fa": "Tiny (فوق‌العاده سریع - کمترین مصرف رم)",
        "en": "Tiny (Ultra Fast - Lowest RAM)"
    },
    "model_base": {
        "fa": "Base (سریع و استاندارد - توصیه شده برای CPU)",
        "en": "Base (Fast & Balanced - Recommended for CPU)"
    },
    "model_small": {
        "fa": "Small (دقت بالا - کیفیت عالی برای فارسی و انگلیسی)",
        "en": "Small (High Accuracy - Great for Persian & English)"
    },
    "model_medium": {
        "fa": "Medium (حداکثر دقت - نیازمند سخت‌افزار قوی)",
        "en": "Medium (Maximum Accuracy - Needs GPU/Strong CPU)"
    },
    # Language Selection
    "language_label": {
        "fa": "زبان گفتار (Language):",
        "en": "Spoken Language:"
    },
    "lang_auto": {
        "fa": "تشخیص خودکار زبان (Auto Detect)",
        "en": "Auto Detect Language"
    },
    "lang_fa": {
        "fa": "فارسی (Persian / Farsi)",
        "en": "Persian (Farsi)"
    },
    "lang_en": {
        "fa": "انگلیسی (English)",
        "en": "English"
    },
    "lang_ar": {
        "fa": "عربی (Arabic)",
        "en": "Arabic"
    },
    "lang_fr": {
        "fa": "فرانسوی (French)",
        "en": "French"
    },
    "lang_de": {
        "fa": "آلمانی (German)",
        "en": "German"
    },
    "lang_es": {
        "fa": "اسپانیایی (Spanish)",
        "en": "Spanish"
    },
    "lang_tr": {
        "fa": "ترکی (Turkish)",
        "en": "Turkish"
    },
    # Subtitle Formats
    "format_label": {
        "fa": "فرمت خروجی زیرنویس:",
        "en": "Output Subtitle Format:"
    },
    "fmt_srt": {
        "fa": "SRT (استاندارد پلیرها و یوتیوب)",
        "en": "SRT (Standard Players & YouTube)"
    },
    "fmt_vtt": {
        "fa": "VTT (استاندارد وب و HTML5)",
        "en": "VTT (Web & HTML5 Video)"
    },
    "fmt_ass": {
        "fa": "ASS (زیرنویس پیشرفته با استایل و رنگ)",
        "en": "ASS (Advanced SubStation with Styles)"
    },
    "fmt_txt": {
        "fa": "TXT (متن خام پیوسته بدون زمان‌بندی)",
        "en": "TXT (Plain Text Transcript)"
    },
    "fmt_json": {
        "fa": "JSON (متادیتای کامل و زمان‌بندی کلمات)",
        "en": "JSON (Full Segments & Word Timestamps)"
    },
    # Subtitle Burn-in
    "burn_group": {
        "fa": "چسباندن زیرنویس روی ویدیو (Hardcode / Burn-in)",
        "en": "Hardcode / Burn Subtitles into Video"
    },
    "burn_enable": {
        "fa": "ایجاد ویدیوی جدید با زیرنویس چسبانده‌شده",
        "en": "Generate new video with burnt-in subtitles"
    },
    "burn_style_tiktok": {
        "fa": "استایل شبکه‌های اجتماعی (کادر زرد/سفید درشت - Reels / TikTok)",
        "en": "Social Media Style (Yellow/White Box - Reels / TikTok)"
    },
    "burn_style_classic": {
        "fa": "استایل کلاسیک سینمایی (زیرنویس با سایه مشکی)",
        "en": "Classic Cinematic Style (Bottom with Outline)"
    },
    "burn_font_size": {
        "fa": "اندازه فونت:",
        "en": "Font Size:"
    },
    # Audio Tools
    "audio_tools_group": {
        "fa": "بهینه‌سازی و پالایش صوت",
        "en": "Audio Processing & Enhancement"
    },
    "vad_filter": {
        "fa": "فیلتر سکوت و تشخیص صدای انسان (VAD Filter)",
        "en": "Silence & Voice Activity Filter (VAD)"
    },
    "audio_normalize": {
        "fa": "نرمال‌سازی بلندی صدا (Loudnorm)",
        "en": "Normalize Audio Loudness"
    },
    "noise_reduction": {
        "fa": "کاهش نویز پس‌زمینه (Noise Reduction)",
        "en": "Background Noise Reduction"
    },
    # Actions & Buttons
    "start_transcribe_btn": {
        "fa": "شروع رونویسی و ساخت زیرنویس",
        "en": "Start Transcription & Generate Subtitles"
    },
    "cancel_btn": {
        "fa": "لغو عملیات",
        "en": "Cancel"
    },
    "preview_tab": {
        "fa": "پیش‌نمایش متن و زمان‌بندی",
        "en": "Transcript Preview & Timestamps"
    },
    "export_btn": {
        "fa": "ذخیره خروجی...",
        "en": "Save Output As..."
    },
    "open_folder": {
        "fa": "نمایش در پوشه خروجی",
        "en": "Show in Explorer"
    },
    "lang_toggle_btn": {
        "fa": "English",
        "en": "فارسی"
    },
    # Status & Progress
    "ready": {
        "fa": "آماده به کار",
        "en": "Ready"
    },
    "loading_model": {
        "fa": "در حال آماده‌سازی مدل هوش مصنوعی ({model})...",
        "en": "Loading AI speech model ({model})..."
    },
    "extracting_audio": {
        "fa": "در حال استخراج و بهینه‌سازی کانال صوتی...",
        "en": "Extracting and optimizing audio track..."
    },
    "transcribing_progress": {
        "fa": "در حال رونویسی هوشمند ({current}/{total} - {percent}%): {name}",
        "en": "Transcribing audio ({current}/{total} - {percent}%): {name}"
    },
    "generating_subtitles": {
        "fa": "در حال قالب‌بندی و ساخت فایل‌های زیرنویس...",
        "en": "Formatting and building subtitle files..."
    },
    "burning_subtitles": {
        "fa": "در حال رندر و چسباندن زیرنویس روی ویدیو با FFmpeg...",
        "en": "Rendering and burning subtitles into video..."
    },
    "completed_success": {
        "fa": "عملیات با موفقیت به پایان رسید!",
        "en": "Transcription completed successfully!"
    },
    "error_empty": {
        "fa": "لطفاً ابتدا حداقل یک فایل ویدیویی یا صوتی انتخاب کنید.",
        "en": "Please select at least one audio or video file first."
    },
    "error_title": {
        "fa": "خطا در پردازش",
        "en": "Processing Error"
    },
    "success_title": {
        "fa": "پایان رونویسی",
        "en": "Transcription Done"
    }
}

_current_language: str = "fa"


def get_current_language() -> str:
    return _current_language


def set_current_language(lang: str) -> None:
    global _current_language
    if lang in ("fa", "en"):
        _current_language = lang


def tr(key: str, lang: Optional[str] = None, **kwargs) -> str:
    active_lang = lang or _current_language
    item = TRANSLATIONS.get(key, {})
    val = item.get(active_lang, item.get("en", key))
    if kwargs:
        try:
            return val.format(**kwargs)
        except Exception:
            return val
    return val

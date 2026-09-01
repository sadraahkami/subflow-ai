# Technical Documentation | مستندات فنی استودیوی SubFlow AI

## ۱. معماری سیستم و لایه‌بندی (System Architecture)

پروژه **SubFlow AI** یک استودیوی چندمنظوره آفلاین برای رونویسی، ساخت زیرنویس و پردازش صوت با هوش مصنوعی محلی است. معماری سیستم از ۵ لایه ماژولار تشکیل شده است:

```
┌─────────────────────────────────────────────────────────────┐
│                 رابط‌های کاربری و دسترسی                     │
│  [PyQt6 Desktop GUI]  /  [Web Studio SPA]  /  [CLI Runner]  │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  هسته پردازشی (Core Engine)                  │
│  ├── Transcriber (Faster-Whisper + Silero VAD)              │
│  ├── Subtitle Exporter (SRT, VTT, ASS, TXT, JSON)           │
│  ├── Subtitle Burner (FFmpeg hardcoding & TikTok presets)   │
│  ├── Audio Processor (Loudness normalize & 16kHz PCM prep)  │
│  └── i18n Engine (Dynamic RTL / LTR Persian & English)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    DevOps و بسته‌بندی                       │
│     [GitHub Actions CI/CD]  /  [Docker]  /  [PyInstaller]   │
└─────────────────────────────────────────────────────────────┘
```

---

## ۲. ساختار جامع فایل‌ها و پوشه‌بندی (Repository Structure)

```text
A:\AGENT\github\SubFlow-AI\
├── .github\
│   └── workflows\
│       └── build-release.yml          # اکشن ساخت خودکار فایل‌های exe و انتشار Release
├── .gitignore                         # قوانین نادیده‌گیری فایل‌های موقت و مدل‌ها
├── Dockerfile                         # ایمیج داکر برای اجرای وب‌استودیو با پشتیبانی FFmpeg
├── docker-compose.yml                 # ارکستراسیون آسان کانتینر
├── LICENSE                            # مجوز رسمی MIT
├── README.md                          # معرفی کامل و ویترین گیت‌هاب (دوزبانه)
├── TECHNICAL_DOCS.md                  # مستندات فنی حاضر
├── BRAIN.md                           # چشم‌انداز محصول و نیازمندی‌های بازار
├── requirements.txt                   # پیش‌نیازهای پایتون
├── main.py                            # نقطه ورود یکپارچه CLI / GUI / Web
├── run_gui.bat                        # اجرای سریع GUI در ویندوز
├── run_web.bat                        # اجرای سریع Web Server در ویندوز
├── build_exe.bat                      # کامپایلر محلی با PyInstaller
├── SubFlowAI.spec                     # کانفیگ بیلد مستقل PyInstaller
├── src\
│   ├── core\
│   │   ├── transcriber.py             # پایپ‌لاین رونویسی گفتار به متن Faster-Whisper
│   │   ├── sub_exporter.py            # تولیدکننده فرمت‌های SRT, VTT, ASS, TXT, JSON
│   │   ├── sub_burner.py              # چسباندن زیرنویس روی ویدیو با FFmpeg
│   │   ├── audio_tools.py             # استخراج صوت، نرمال‌سازی صدا و بررسی مدت‌زمان
│   │   ├── validator.py               # اعتبارسنجی فرمت‌های چندرسانه‌ای و استخراج متادیتا
│   │   └── i18n.py                    # موتور ترجمه و سوئیچ آنی زبان فارسی و انگلیسی
│   ├── gui\
│   │   ├── main_window.py             # پنجره اصلی PyQt6 با پردازش ناهمگام QThread
│   │   ├── widgets.py                 # کارت‌های مدیا، دراپ‌زون فایل‌ها و کنترل‌ها
│   │   ├── icons.py                   # مدیریت کش برداری آیکون‌های SVG
│   │   └── styles.py                  # استایل‌های دارک نئونی و قوانین RTL
│   ├── web\
│   │   ├── server.py                  # سرور HTTP استاندارد با اندپوینت‌های REST
│   │   └── static\
│   │       ├── index.html             # رابط کاربری مدرن SPA
│   │       ├── style.css              # استایل‌های شیشه‌ای (Glassmorphism)
│   │       └── app.js                 # منطق کلاینت، دراگ‌انددراپ و دانلود زیرنویس
│   └── cli\
│       └── cli_runner.py              # پردازشگر پیشرفته خط فرمان
└── tests\
    ├── test_sub_exporter.py           # تست‌های فرمت‌بندی SRT, VTT, ASS, JSON
    ├── test_audio_tools.py            # تست استخراج و آماده‌سازی صوت
    ├── test_transcriber.py            # تست ساختارهای داده و پایپ‌لاین
    └── test_validator.py              # تست اعتبارسنجی پسوندها و بازرسی فایل
```

---

## ۳. شرح فنی ماژول‌ها

### ۳.۱. موتور رونویسی گفتار (`src/core/transcriber.py`)
- استفاده از ساختارهای داده‌ای `TranscriptionSegment` و `WordTimestamp`.
- انتخاب خودکار سخت‌افزار (NVIDIA CUDA در صورت وجود، یا پردازنده مرکزی CPU با کوانتیزاسیون سریع `int8`).
- فیلتر `vad_filter` جهت حذف هذیان‌های مدل در فواصل سکوت طولانی.
- سیستم Fail-Safe و Mock داخلی برای اجرای روان تست‌های واحد در محیط‌های CI بدون نیاز به دانلود مدل‌های حجیم.

### ۳.۲. صادرکننده زیرنویس (`src/core/sub_exporter.py`)
- محاسبه دقیق میلی‌ثانیه‌ها در فرمت استاندارد SubRip (`00:00:00,000`) و WebVTT (`00:00:00.000`).
- تولید ساختار پیشرفته ASS با هدرهای استاندارد، سایه‌گذاری و استایل مخصوص برای سازگاری با انکودرهای ویدیویی.

### ۳.۳. پردازشگر صوت و چسباندن زیرنویس (`src/core/audio_tools.py` & `src/core/sub_burner.py`)
- تبدیل تمام فرمت‌های ورودی به بایت‌های خام 16kHz PCM Mono WAV.
- فیلتر نرمال‌سازی بلندی صدا بر اساس استاندارد EBU R128 (`loudnorm=I=-16:TP=-1.5:LRA=11`).
- انکودینگ دوطرفه زیرنویس در FFmpeg با اسکیپ صحیح کاراکترهای مسیر در سیستم‌عامل ویندوز.

---

## ۴. راستی‌آزمایی و نتایج تست‌ها

اجرای تست‌های واحد خودکار با دستور:
```bash
cmd /c python -m unittest discover tests
```
- **۱۱ تست خودکار** شامل تولید زیرنویس، زمان‌بندی‌ها، استخراج صوت، اعتبارسنجی فرمت‌ها و یکپارچه‌سازی بدون خطا پاس شدند.

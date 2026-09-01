# 🎙️ SubFlow AI | Offline Speech Transcription & Subtitle Studio
### استودیوی هوشمند و آفلاین رونویسی گفتار و تولید زیرنویس

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![GUI: PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52.svg)](https://pypi.org/project/PyQt6/)
[![AI Engine: Faster--Whisper](https://img.shields.io/badge/AI-Faster--Whisper-orange.svg)](https://github.com/SYSTRAN/faster-whisper)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)](.github/workflows/build-release.yml)

An all-in-one, high-performance, 100% offline speech-to-text suite, subtitle generator, and audio enhancement studio. Featuring AI-powered Faster-Whisper transcription, multi-format subtitle export (SRT, VTT, ASS, JSON, TXT), animated social media (TikTok/Reels) subtitle burning, modern PyQt6 desktop GUI, web SPA, and Docker deployment.

یک استودیوی جامع، فوق‌العاده سریع و ۱۰۰٪ آفلاین برای تبدیل صوت و ویدیو به متن و زیرنویس؛ شامل رونویسی هوش مصنوعی با پشتیبانی کامل از زبان فارسی و انگلیسی، خروجی در فرمت‌های متنوع زیرنویس (SRT، VTT، ASS، JSON)، چسباندن زیرنویس متحرک روی ویدیو (سبک اینستاگرام و تیک‌تاک)، رابط دسکتاپ PyQt6، وب‌سرور تک‌صفحه‌ای و کانتینر داکر.

---

## 🌟 Highlights / قابلیت‌های شاخص

| Feature / قابلیت | Description / توضیحات |
| :--- | :--- |
| ⚡ **100% Offline AI** | Runs locally without cloud API costs or internet requirements (Faster-Whisper INT8/FP16). |
| 🌐 **90+ Languages** | Automatic language detection with deep support for **Persian (فارسی RTL)** and **English**. |
| 🎬 **Subtitle Burning** | Hardcode animated, stylized subtitles (TikTok/Reels Yellow Box or Cinematic) directly into MP4 videos with FFmpeg. |
| 📄 **Multi-Format Export** | Export transcripts instantly as **SRT**, **VTT**, **ASS**, **Plain TXT**, and **JSON with word-level timestamps**. |
| 🧹 **Audio Optimizer** | Voice Activity Detection (VAD) silence filter, loudness normalization, and noise suppression. |
| 🖥️ **PyQt6 Desktop & Web SPA** | Modern dark-themed native desktop UI + built-in responsive browser studio. |
| 🐳 **Docker Microservice** | Ready-to-deploy container with single-command `docker-compose up -d`. |

---

## 🌐 Navigation / فهرست

- [English Guide](#-english-guide)
  - [Quick Start](#-quick-start)
  - [CLI Examples](#-cli-examples)
- [راهنمای فارسی](#-راهنمای-فارسی)
  - [شروع سریع](#-شروع-سریع)
  - [واسط خط فرمان (CLI)](#-واسط-خط-فرمان-cli)
- [Docker Deployment](#-docker-deployment)
- [License](#-license)

---

## 🇬🇧 English Guide

### 🚀 Quick Start

#### 1. Desktop Application (PyQt6)
Double-click `run_gui.bat` or execute:
```bash
python main.py
```

#### 2. Web Studio (Single Page App)
Double-click `run_web.bat` or run:
```bash
python main.py --web
```
Open `http://localhost:8080` in your browser.

#### 3. Command-Line Interface (CLI)
```bash
# Transcribe speech to Persian SRT using base model:
python main.py interview.mp3 --lang fa --format srt -o output.srt

# Transcribe video and burn TikTok-style subtitles:
python main.py podcast.mp4 --model small --burn -o ./output/
```

---

## 🇮🇷 راهنمای فارسی

### 🚀 شروع سریع

#### ۱. اجرای نرم‌افزار دسکتاپ (PyQt6)
با دو بار کلیک روی `run_gui.bat` یا دستور زیر در ترمینال:
```bash
python main.py
```

#### ۲. اجرای استودیوی تحت وب (Web Studio)
با دو بار کلیک روی `run_web.bat` یا دستور:
```bash
python main.py --web
```
سپس آدرس `http://localhost:8080` را در مرورگر باز کنید.

#### ۳. واسط خط فرمان (CLI)
```bash
# رونویسی صوت به زیرنویس فارسی با فرمت SRT:
python main.py voice.mp3 --lang fa --format srt -o result.srt

# رونویسی و چسباندن خودکار زیرنویس با فونت درشت روی ویدیو (مخصوص ریلز/یوتیوب):
python main.py clip.mp4 --model small --burn
```

---

## 🐳 Docker Deployment

```bash
docker-compose up -d
```
Your local SubFlow AI web studio will be running at `http://localhost:8080`.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

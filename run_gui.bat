@echo off
title SubFlow AI - Speech & Subtitle Studio
echo Starting SubFlow AI GUI Desktop...
python main.py
if errorlevel 1 (
    echo.
    echo An error occurred. If PyQt6 is missing, run: pip install -r requirements.txt
    pause
)

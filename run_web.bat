@echo off
title SubFlow AI - Web Studio
echo Starting SubFlow AI Web Studio...
python main.py --web
if errorlevel 1 (
    echo.
    echo An error occurred while starting web server.
    pause
)

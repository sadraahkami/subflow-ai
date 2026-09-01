@echo off
title Build SubFlow AI Standalone Executable
echo ===================================================
echo   Compiling SubFlow AI to Single-File Portable EXE
echo ===================================================
echo.
pip install pyinstaller -q
pyinstaller SubFlowAI.spec --noconfirm --clean
echo.
echo Build finished! Executable is located in dist/SubFlowAI.exe
pause

@echo off
REM Image Duplicate Finder v2.3 - GUI Launcher

echo.
echo =========================================
echo   🔍 IMAGE DUPLICATE FINDER v2.3
echo   🎨 Sistema Temi Avanzato
echo =========================================
echo.

REM Verifica che Python sia installato
if not exist ".venv\Scripts\python.exe" (
    echo ERRORE: Ambiente virtuale Python non trovato!
    echo Eseguire prima: python -m venv .venv
    echo Poi: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo Avvio interfaccia grafica...
".venv\Scripts\python.exe" gui_interface.py

echo.
echo Interfaccia chiusa.
pause

@echo off
REM Avvia l'interfaccia web

echo.
echo =======================================
echo   IMAGE DUPLICATE FINDER - WEB
echo =======================================
echo.

REM Verifica che Python sia installato
if not exist ".venv\Scripts\python.exe" (
    echo ERRORE: Ambiente virtuale Python non trovato!
    echo Provo con python di sistema...
    echo.
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERRORE: Python non trovato nel sistema!
        echo Installa Python o configura l'ambiente virtuale
        pause
        exit /b 1
    )
    echo Uso Python di sistema...
    python web_interface.py
) else (
    echo Uso ambiente virtuale Python...
    ".venv\Scripts\python.exe" web_interface.py
)

echo.
echo Apri il browser su: http://localhost:5000
echo.
echo Premi Ctrl+C per fermare il server
echo.

pause

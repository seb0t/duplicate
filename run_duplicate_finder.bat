@echo off
REM Script batch per avviare Image Duplicate Finder su Windows

echo.
echo =======================================
echo   IMAGE DUPLICATE FINDER
echo =======================================
echo.

REM Verifica che Python sia installato
if not exist ".venv\Scripts\python.exe" (
    echo ERRORE: Ambiente virtuale Python non trovato!
    echo Eseguire prima: python -m venv .venv
    echo Poi: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Chiedi la cartella da scansionare
set /p FOLDER="Inserisci il percorso della cartella da scansionare: "

if "%FOLDER%"=="" (
    echo ERRORE: Percorso cartella non specificato!
    pause
    exit /b 1
)

REM Verifica se la cartella esiste
if not exist "%FOLDER%" (
    echo ERRORE: La cartella '%FOLDER%' non esiste!
    pause
    exit /b 1
)

echo.
echo Avvio ricerca duplicati in: %FOLDER%
echo.

REM Esegui il programma
".venv\Scripts\python.exe" image_duplicate_finder.py "%FOLDER%" --verbose

echo.
echo Operazione completata! Premi un tasto per chiudere...
pause >nul

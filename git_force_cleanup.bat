@echo off
REM Script avanzato per rimuovere dal Git i file ora ignorati

echo.
echo ==========================================
echo   🧹 GIT FORCE CLEANUP - RIMOZIONE CACHE
echo ==========================================
echo.

echo ⚠️  ATTENZIONE: Questo rimuoverà dal Git tutti i file
echo     che sono ora nel .gitignore ma erano tracciati prima
echo.
set /p confirm="Continuare? (y/N): "
if /i not "%confirm%"=="y" (
    echo Operazione annullata.
    pause
    exit /b 0
)

echo.
echo 🗂️ Rimuovo cache Git per file ignorati...
git rm -r --cached .

echo.
echo 📁 Ri-aggiungo tutti i file (rispettando .gitignore)...
git add .

echo.
echo 📋 Stato dopo la pulizia:
git status

echo.
echo 📝 Vuoi committare le modifiche? (y/N): 
set /p commit_confirm=""
if /i "%commit_confirm%"=="y" (
    git commit -m "🧹 Pulizia repository: rimossi file ignorati dalla cache Git"
    echo.
    echo 🚀 Vuoi fare push? (y/N): 
    set /p push_confirm=""
    if /i "%push_confirm%"=="y" (
        git push
        echo ✅ Push completato!
    )
)

echo.
echo ✅ Pulizia avanzata completata!
pause

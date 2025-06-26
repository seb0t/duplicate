@echo off
REM Script per pulire il repository Git da file eliminati

echo.
echo ==========================================
echo   🧹 GIT CLEANUP - PULIZIA REPOSITORY
echo ==========================================
echo.

echo 📋 Stato attuale del repository:
git status

echo.
echo 🗑️ Rimuovo file eliminati dal tracking Git...
git add -A

echo.
echo 📝 Commit delle modifiche...
git commit -m "Pulizia progetto: rimossi file di test, demo e documentazione temporanea"

echo.
echo 🚀 Push delle modifiche...
git push

echo.
echo ✅ Pulizia completata!
echo.

pause

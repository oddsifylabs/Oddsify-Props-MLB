@echo off
REM Push to GitHub - Run this on any Windows machine with git installed

echo.
echo 🚀 Pushing Oddsify Props to GitHub...
echo.

REM Set remote
git remote add origin https://github.com/oddsifylabs/Oddsify-Props-MLB.git 2>nul
if errorlevel 1 (
    git remote set-url origin https://github.com/oddsifylabs/Oddsify-Props-MLB.git
)

REM Ensure main branch
git branch -M main

REM Push
echo 📤 Pushing commits to GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ❌ Push failed. Check your internet connection and GitHub credentials.
    pause
    exit /b 1
)

echo.
echo ✅ SUCCESS!
echo.
echo Your repo is live at:
echo    https://github.com/oddsifylabs/Oddsify-Props-MLB
echo.
echo Recent commits:
git log --oneline -3
echo.
pause

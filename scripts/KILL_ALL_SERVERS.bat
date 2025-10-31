@echo off
echo ============================================================
echo Killing ALL ConvoSynth server processes
echo ============================================================
echo.

taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [OK] All Python processes killed
echo.
echo Now run: python run.py
echo.
pause

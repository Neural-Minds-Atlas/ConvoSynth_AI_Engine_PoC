@echo off
echo ============================================================
echo ConvoSynth - Restart and Test Script
echo ============================================================
echo.
echo This script will:
echo 1. Kill any running servers
echo 2. Start fresh server
echo 3. Wait for startup
echo 4. Run comprehensive tests
echo.
pause

echo.
echo [Step 1] Killing any running servers...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *run.py*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo [Step 2] Starting ConvoSynth server...
start "ConvoSynth Server" cmd /k "python run.py"

echo.
echo [Step 3] Waiting for server startup (15 seconds)...
timeout /t 15 /nobreak

echo.
echo [Step 4] Running comprehensive tests...
python test_rag_complete.py

echo.
echo ============================================================
echo Tests Complete!
echo ============================================================
echo.
echo Check the output above for results.
echo Generated HTML files should be in the current directory.
echo.
pause

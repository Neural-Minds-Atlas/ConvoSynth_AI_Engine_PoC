@echo off
REM ConvoSynth Backend Startup Script for Windows

echo ======================================
echo   ConvoSynth Backend Startup
echo ======================================
echo.

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env > nul
    echo [OK] .env file created
    echo.
    echo [IMPORTANT] You need to add your Anthropic API key to .env
    echo    Edit .env and add: ANTHROPIC_API_KEY=your_key_here
    echo.
    pause
)

REM Check if Docker is running
docker info > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo    Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Check if API key is set
findstr /C:"your_anthropic_api_key_here" .env > nul
if not errorlevel 1 (
    echo [WARNING] Anthropic API key not set in .env
    echo    The backend will fail without a valid API key
    echo.
    set /p confirm="Continue anyway? (y/N): "
    if /i not "%confirm%"=="y" (
        echo Aborted. Please add your API key to .env first.
        pause
        exit /b 1
    )
)

echo Starting services with Docker Compose...
echo.

REM Start services
docker-compose up -d

echo.
echo [WAIT] Waiting for services to be ready...
echo    This may take 30-60 seconds on first run...
echo.

REM Wait for backend
set max_attempts=30
set attempt=0

:wait_loop
if %attempt% GEQ %max_attempts% goto timeout

curl -sf http://localhost:8000/health > nul 2>&1
if errorlevel 1 (
    set /a attempt+=1
    timeout /t 2 /nobreak > nul
    echo|set /p="."
    goto wait_loop
)

echo.
echo [OK] Backend is ready!
echo.

REM Check database
curl -sf http://localhost:8000/health/db 2>nul | findstr /C:"healthy" > nul
if not errorlevel 1 (
    echo [OK] MongoDB is connected
) else (
    echo [WARNING] MongoDB connection failed
    echo    Check logs: docker-compose logs mongodb
)

goto success

:timeout
echo.
echo.
echo [WARNING] Backend did not start within expected time
echo    Check logs: docker-compose logs backend
echo.
pause
exit /b 1

:success
echo.
echo ======================================
echo   ConvoSynth Backend is Running!
echo ======================================
echo.
echo Access points:
echo   * Backend API:     http://localhost:8000
echo   * API Docs:        http://localhost:8000/docs
echo   * Health Check:    http://localhost:8000/health
echo   * MongoDB:         localhost:27017
echo.
echo Quick commands:
echo   * View logs:       docker-compose logs -f backend
echo   * Stop services:   docker-compose down
echo   * Test API:        python example_client.py
echo.
echo Next steps:
echo   1. Visit http://localhost:8000/docs to see API documentation
echo   2. Run: python example_client.py to test the system
echo   3. Read QUICKSTART.md for more information
echo.
echo ======================================
echo.
pause

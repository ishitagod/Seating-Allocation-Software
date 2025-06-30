@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: ============================================
:: Seat Allocation Software - Start Script
:: ============================================

:: Check for required commands
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    pause
    exit /b 1
)

:: Set Paths and Variables
SET "ROOT=%~dp0"
SET "BACKEND_DIR=%ROOT%backend"
SET "FRONTEND_DIR=%ROOT%exam-seating-app"
SET "VENV_ACTIVATE=%ROOT%venv\Scripts\activate.bat"
SET "BACKEND_URL=http://localhost:8000"
SET "FRONTEND_URL=http://localhost:5173"

:: Check if directories exist
if not exist "%BACKEND_DIR%" (
    echo [ERROR] Backend directory not found at %BACKEND_DIR%
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo [ERROR] Frontend directory not found at %FRONTEND_DIR%
    pause
    exit /b 1
)

:: Setup Python Virtual Environment
if not exist "%ROOT%venv" (
    echo [INFO] Creating virtual environment...
    python -m venv "%ROOT%venv"
    if !ERRORLEVEL! NEQ 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    call "%VENV_ACTIVATE%"
    echo [INFO] Installing Python dependencies...
    pip install -r "%ROOT%requirements.txt"
    if !ERRORLEVEL! NEQ 0 (
        echo [ERROR] Failed to install Python dependencies
        pause
        exit /b 1
    )
)

:: Start Backend Server
echo [INFO] Starting backend server...
start "Backend" cmd /k "cd /d "%BACKEND_DIR%" && call "%VENV_ACTIVATE%" && python app.py || (echo [ERROR] Backend failed to start && pause)"

:: Start Frontend
timeout /t 2 /nobreak >nul
echo [INFO] Starting frontend development server...
if not exist "%FRONTEND_DIR%\node_modules" (
    echo [INFO] Installing frontend dependencies...
    cd /d "%FRONTEND_DIR%" && npm install
    if !ERRORLEVEL! NEQ 0 (
        echo [ERROR] Failed to install frontend dependencies
        pause
        exit /b 1
    )
)

start "Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && echo [FRONTEND] Starting development server... && start "" "%FRONTEND_URL%" && npm run dev || (echo [ERROR] Frontend failed to start && pause)"

:: Show completion message
cls
echo ============================================
echo  SEAT ALLOCATION SOFTWARE - RUNNING
echo ============================================
echo.
echo  [STATUS] Application is running in separate windows
echo.
echo  - Backend:  %BACKEND_URL%
echo  - Frontend: %FRONTEND_URL%
echo.
echo  [INSTRUCTIONS]
echo  1. Check both console windows for any errors
echo  2. The application should open in your default browser
echo  3. If not, manually open: %FRONTEND_URL%
echo  4. Close all windows to stop the application
echo.
echo  [TROUBLESHOOTING]
echo  - If you see any errors in the console windows:
echo    1. Take note of the error message
echo    2. Close all console windows
:wait
choice /c Q /m "Press Q to quit and close all windows"
if errorlevel 2 goto wait

echo.
echo [INFO] Cleaning up...
taskkill /F /FI "WINDOWTITLE eq Backend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Frontend*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq npm*" >nul 2>&1
echo [INFO] All processes have been terminated.

ENDLOCAL
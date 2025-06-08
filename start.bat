@echo off
REM ============================================
REM Seat Allocation Software - Start Script
REM ============================================

SETLOCAL

REM ─────────────────────────────────────────────
REM 1) Set Paths
REM ─────────────────────────────────────────────
SET "ROOT=%~dp0"
SET "BACKEND_DIR=%ROOT%backend"
SET "FRONTEND_DIR=%ROOT%exam-seating-app"
SET "VENV_ACTIVATE=%ROOT%venv\Scripts\activate.bat"

REM ─────────────────────────────────────────────
REM 2) Check if directories exist
REM ─────────────────────────────────────────────
if not exist "%BACKEND_DIR%" (
    echo Error: Backend directory not found at %BACKEND_DIR%
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo Error: Frontend directory not found at %FRONTEND_DIR%
    pause
    exit /b 1
)

REM ─────────────────────────────────────────────
REM 3) Setup Python Virtual Environment
REM ─────────────────────────────────────────────
if not exist "%ROOT%venv" (
    echo Creating virtual environment...
    python -m venv "%ROOT%venv"
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
    call "%VENV_ACTIVATE%"
    echo Installing Python dependencies...
    pip install -r "%ROOT%requirements.txt"
) else (
    call "%VENV_ACTIVATE%"
)

REM ─────────────────────────────────────────────
REM 4) Start Backend Server (hidden)
REM ─────────────────────────────────────────────
start "" /B cmd /c "cd /d "%BACKEND_DIR%" && python app.py"

REM ─────────────────────────────────────────────
REM 5) Start Frontend in a new window
REM ─────────────────────────────────────────────
start "Frontend" cmd /k "@echo off && cd /d "%FRONTEND_DIR%" && echo [FRONTEND] Installing dependencies... && npm install && echo [FRONTEND] Starting development server... && start http://localhost:5173 && echo [FRONTEND] Server starting on http://localhost:5173 && npm run dev"

REM ─────────────────────────────────────────────
REM 6) Wait for backend to start
REM ─────────────────────────────────────────────
timeout /t 5 /nobreak >nul

REM ─────────────────────────────────────────────
REM 7) Show completion message
REM ─────────────────────────────────────────────
echo.
echo ============================================
echo  Seat Allocation Software is starting...
echo  - Backend:  http://localhost:8000
echo  - Frontend: http://localhost:5173
echo.
echo  Please check the frontend window for progress.
echo  If browser doesn't open automatically, please open:
echo  http://localhost:5173 manually
echo.
echo  Note: First startup may take a few minutes for dependencies.
echo.
echo  Press any key to close this window.
echo ============================================
pause > nul

ENDLOCAL

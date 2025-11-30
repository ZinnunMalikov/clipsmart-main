@echo off
REM ClipSmart Installation Script for Windows
REM This script installs ClipSmart and its dependencies

echo Installing ClipSmart...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.8+ is required but not installed.
    echo Please install Python 3.8 or higher and try again.
    pause
    exit /b 1
)

echo Python detected

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip is required but not installed.
    echo Please install pip and try again.
    pause
    exit /b 1
)

REM Ask about virtual environment
set /p create_venv="Create a virtual environment? (recommended) [y/N]: "
if /i "%create_venv%"=="y" (
    echo Creating virtual environment...
    python -m venv clipsmart-env
    call clipsmart-env\Scripts\activate
    echo Virtual environment activated
    echo To activate later, run: clipsmart-env\Scripts\activate
)

REM Install ClipSmart
echo Installing ClipSmart package...
pip install -e .

echo.
echo ClipSmart installed successfully!
echo.
echo Next steps:
echo 1. Set your API keys in environment variables:
echo    set GENAI_API_KEY=your-gemini-api-key
echo    set AWS_ACCESS_KEY_ID=your-aws-key
echo    set AWS_SECRET_ACCESS_KEY=your-aws-secret
echo.
echo 2. Start the server:
echo    uvicorn backend.processing.main:app --host 0.0.0.0 --port 8000
echo.
echo 3. Access the API at: http://localhost:8000
echo.
echo For more information, see the README.md file
pause
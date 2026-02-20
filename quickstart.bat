@echo off
REM Quick Start Script for Location Safety RAG API

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Location Safety RAG - Quick Start Script             ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if venv exists
if not exist "venv" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated

echo.
echo [3/4] Installing dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo [4/4] Initializing database...
python app/database/init.py
if errorlevel 1 (
    echo ⚠️  Database initialization had issues (this might be OK if DB already exists)
)
echo ✅ Database ready

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Setup Complete! Starting Server...                   ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo 📖 Swagger Docs: http://localhost:8000/docs
echo 📖 ReDoc Docs: http://localhost:8000/redoc
echo 🔗 API: http://localhost:8000
echo.
echo Press CTRL+C to stop the server
echo.

uvicorn app.main:app --reload

pause

@echo off
REM Movie Recommender System - Startup Script
REM This script starts both FastAPI and Streamlit in separate windows

echo.
echo ====================================================
echo   Movie Recommender System - Startup Script
echo ====================================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call .\rec\Scripts\Activate.ps1
    if errorlevel 1 (
        echo Error: Failed to activate virtual environment
        pause
        exit /b 1
    )
)

echo.
echo Starting FastAPI backend server...
echo Opening new window for API...
start "Movie Recommender API" cmd /k python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload

timeout /t 3

echo.
echo Starting Streamlit frontend...
echo Opening new window for Frontend...
start "Movie Recommender Frontend" cmd /k streamlit run app.py

echo.
echo ====================================================
echo   Both services are starting...
echo.
echo   API Documentation: http://127.0.0.1:8000/docs
echo   Frontend App: http://localhost:8501
echo.
echo   Close these windows when done.
echo ====================================================
echo.

pause

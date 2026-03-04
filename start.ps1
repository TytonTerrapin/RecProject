# Movie Recommender System - Startup Script (PowerShell)
# This script starts both FastAPI and Streamlit in separate windows

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   Movie Recommender System - Startup Script" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if ($null -eq $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\rec\Scripts\Activate.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to activate virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "Starting FastAPI backend server..." -ForegroundColor Green
Write-Host "Opening new window for API..." -ForegroundColor Yellow

# Start FastAPI in a new PowerShell window
$apiProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload" -WindowStyle Normal -PassThru

Start-Sleep -Seconds 3

Write-Host "Starting Streamlit frontend..." -ForegroundColor Green
Write-Host "Opening new window for Frontend..." -ForegroundColor Yellow

# Start Streamlit in a new PowerShell window
$appProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run app.py" -WindowStyle Normal -PassThru

Write-Host ""
Write-Host "====================================================" -ForegroundColor Green
Write-Host "   Both services are starting..." -ForegroundColor Green
Write-Host ""
Write-Host "   API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "   Frontend App: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Close the spawned windows when done." -ForegroundColor Yellow
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Press Ctrl+C to stop this script (but not the running services)..."

# Wait indefinitely
while ($true) {
    Start-Sleep -Seconds 1
}

@echo off
title IntentCart — AI Fashion Discovery Engine
echo ======================================================================
echo           Starting IntentCart (FastAPI + React Vite)
echo ======================================================================
echo.

start "IntentCart Backend (FastAPI)" cmd /k "cd /d %~dp0 && .\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 >nul

start "IntentCart Frontend (Vite)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo Backend URL:  http://127.0.0.1:8000
echo Frontend URL: http://localhost:5173/
echo.
echo Both services are now running in their respective terminal windows.
echo ======================================================================

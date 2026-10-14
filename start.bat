@echo off
setlocal

echo [PowerTracker] Starting Servers...

:: Check if PostgreSQL is reachable on port 5432
netstat -ano | findstr :5432 >nul
if %errorlevel% neq 0 (
    echo [WARNING] PostgreSQL does not appear to be running on port 5432.
    echo [WARNING] The backend might fail to start if the database service is off.
    echo [ACTION] Please ensure PostgreSQL is started in Windows Services.
    echo.
    choice /M "Try starting anyway?"
    if errorlevel 2 exit /b
)

:: Activate Virtual Environment and Start Django Backend in a new window
echo [PowerTracker] Starting Django Backend...
start "PowerTracker Backend" cmd /k "call .\powertracker\Scripts\activate.bat && python manage.py runserver"

:: Start Vite Frontend in a new window
echo [PowerTracker] Starting React Frontend...
start "PowerTracker Frontend" cmd /k "cd frontend && npm run dev"

echo [PowerTracker] Servers are starting in separate windows.
echo [PowerTracker] Close the windows to stop the servers, or run stop.bat.
pause

@echo off
echo [PowerTracker] Starting Docker Environment...
echo [PowerTracker] Ensuring local servers are stopped (to free up ports)...
call stop.bat

echo [PowerTracker] Building and Scaling Rathinam PowerTracker...
docker-compose up --build -d

echo.
echo [PowerTracker] Environments is starting!
echo [PowerTracker] Backend: http://localhost:8000
echo [PowerTracker] Frontend: http://localhost:5173
echo.
echo [PowerTracker] Use "docker-compose logs -f" to see real-time logs.
echo [PowerTracker] Use "docker-compose down" to stop everything.
pause

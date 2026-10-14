@echo off
echo [PowerTracker] Stopping Servers and Containers...

:: Kill python processes (Django)
taskkill /IM python.exe /F 2>nul
:: Kill node processes (Vite/NPM)
taskkill /IM node.exe /F 2>nul

:: Stop and remove Docker containers
echo [PowerTracker] Shutting down Docker containers...
docker-compose down

echo [PowerTracker] Servers and containers stopped.

@echo off
REM AI Education Assistant Backend Stop Script for Windows

echo 🛑 Stopping AI Education Assistant Backend...

REM Stop services with Docker Compose
echo 🐳 Stopping services...
docker-compose down

REM Check if services are stopped
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Some services are still running. Force stopping...
    docker-compose down --remove-orphans
) else (
    echo ✅ All services stopped successfully!
)

echo.
echo 📋 Service Status:
docker-compose ps

pause


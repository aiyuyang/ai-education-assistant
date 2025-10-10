@echo off
REM AI Education Assistant Backend Startup Script for Windows

echo 🚀 Starting AI Education Assistant Backend...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Copying from env.example...
    copy env.example .env
    echo 📝 Please edit .env file with your configuration before running again.
    pause
    exit /b 1
)

REM Start services with Docker Compose
echo 🐳 Starting services with Docker Compose...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo ✅ Services started successfully!
    echo.
    echo 📋 Service Status:
    docker-compose ps
    echo.
    echo 🌐 API Documentation:
    echo    - Swagger UI: http://localhost:8000/docs
    echo    - ReDoc: http://localhost:8000/redoc
    echo.
    echo 📊 Service URLs:
    echo    - API Server: http://localhost:8000
    echo    - MySQL: localhost:3306
    echo    - Redis: localhost:6379
    echo.
    echo 📝 To view logs: docker-compose logs -f app
    echo 🛑 To stop services: docker-compose down
) else (
    echo ❌ Failed to start services. Check logs with: docker-compose logs
    pause
    exit /b 1
)

pause


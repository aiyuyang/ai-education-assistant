@echo off
REM Test runner script for AI Education Assistant (Windows)

echo 🧪 Running AI Education Assistant Tests
echo ========================================

REM Check if we're in a virtual environment
if defined VIRTUAL_ENV (
    echo ✅ Virtual environment detected: %VIRTUAL_ENV%
) else (
    echo ⚠️  No virtual environment detected. Consider using one.
)

REM Install test dependencies if needed
echo 📦 Installing test dependencies...
pip install pytest pytest-asyncio pytest-cov httpx

REM Run tests with coverage
echo 🚀 Running tests with coverage...
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=80 -v --tb=short

REM Check test results
if %ERRORLEVEL% EQU 0 (
    echo ✅ All tests passed!
    echo 📊 Coverage report generated in htmlcov/
    echo 🌐 Open htmlcov/index.html to view detailed coverage report
) else (
    echo ❌ Some tests failed!
    exit /b 1
)


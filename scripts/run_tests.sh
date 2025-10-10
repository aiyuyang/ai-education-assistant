#!/bin/bash

# Test runner script for AI Education Assistant

echo "🧪 Running AI Education Assistant Tests"
echo "========================================"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Consider using one."
fi

# Install test dependencies if needed
echo "📦 Installing test dependencies..."
pip install pytest pytest-asyncio pytest-cov httpx

# Run tests with coverage
echo "🚀 Running tests with coverage..."
pytest tests/ \
    --cov=app \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-fail-under=80 \
    -v \
    --tb=short

# Check test results
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
    echo "📊 Coverage report generated in htmlcov/"
    echo "🌐 Open htmlcov/index.html to view detailed coverage report"
else
    echo "❌ Some tests failed!"
    exit 1
fi


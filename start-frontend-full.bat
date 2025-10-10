@echo off
echo Starting AI Education Assistant Frontend...
cd /d "E:\ai-education-assistant\frontend"
echo Current directory: %CD%
echo.
echo Checking if node_modules exists...
if exist "node_modules" (
    echo node_modules found
) else (
    echo node_modules not found, installing dependencies...
    npm install
)
echo.
echo Starting React development server...
echo This may take a few minutes...
npm start


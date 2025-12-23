@echo off
REM Setup script for Raspberry Pi Banking Terminal Frontend

echo Setting up Raspberry Pi Banking Terminal Frontend...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed. Please install Node.js first.
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo npm is not installed. Please install Node.js (which includes npm) first.
    exit /b 1
)

REM Install dependencies
echo Installing frontend dependencies...
npm install

REM Check if installation was successful
if %errorlevel% equ 0 (
    echo Frontend dependencies installed successfully!
    
    echo To start the development server, run:
    echo   npm start
    echo.
    echo To build for production, run:
    echo   npm run build
    echo.
    echo To integrate with the Flask backend, run the build script:
    echo   build.bat
) else (
    echo Failed to install frontend dependencies.
    exit /b 1
)
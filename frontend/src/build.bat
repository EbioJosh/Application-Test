@echo off
REM Build script to integrate React frontend with Flask backend

echo Building React frontend for Raspberry Pi Banking Terminal...

REM Create build directory if it doesn't exist
if not exist "..\app\static" mkdir "..\app\static"

REM Build React app
npm run build

REM Copy build files to Flask static directory
xcopy /E /I /Y build\* ..\app\static\

echo Frontend build complete!
echo Files copied to ..\app\static\
echo The Flask backend will now serve the React frontend.
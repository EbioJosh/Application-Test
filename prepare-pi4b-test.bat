@echo off
REM Prepare Raspberry Pi 4B Test Environment Package

echo ===============================================
echo Preparing Raspberry Pi 4B Test Environment Package
echo ===============================================

REM Create deployment package directory
echo Creating deployment package directory...
mkdir pi4b-test-package

REM Copy essential files
echo Copying files to package...
copy setup-pi4b-test.sh pi4b-test-package\
copy requirements.txt pi4b-test-package\

REM Create a zip file
echo Creating zip archive...
powershell Compress-Archive -Path pi4b-test-package\* -DestinationPath rpi4b-hardware-test.zip -Force

echo ===============================================
echo Package created: rpi4b-hardware-test.zip
echo ===============================================
echo Transfer Instructions:
echo 1. Transfer this file to your Raspberry Pi 4B:
echo    scp rpi4b-hardware-test.zip pi@your-pi-ip:/home/pi/
echo 2. On your Raspberry Pi, extract and run:
echo    unzip rpi4b-hardware-test.zip
echo    cd pi4b-test-package
echo    chmod +x setup-pi4b-test.sh
echo    ./setup-pi4b-test.sh
echo ===============================================

echo Cleanup...
rmdir /S /Q pi4b-test-package

echo Ready for Raspberry Pi 4B test deployment!
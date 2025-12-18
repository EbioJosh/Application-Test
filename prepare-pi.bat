@echo off
REM Prepare Raspberry Pi package for transfer

echo Preparing Raspberry Pi package...

REM Create a deployment package
echo Creating deployment package...
mkdir deploy-package
mkdir deploy-package\app

REM Copy essential files
copy requirements.txt deploy-package\
copy run.py deploy-package\
copy rpi-hardware-appliance.service deploy-package\
copy setup-pi.sh deploy-package\setup.sh

REM Copy app directory
xcopy /E /I app deploy-package\app

REM Create a zip file
echo Creating zip archive...
powershell Compress-Archive -Path deploy-package\* -DestinationPath rpi-hardware-appliance.zip -Force

echo Package created: rpi-hardware-appliance.zip
echo Transfer this file to your Raspberry Pi and extract it.
echo Then run: bash setup.sh

echo Cleanup...
rmdir /S /Q deploy-package

echo Ready for Raspberry Pi deployment!
@echo off
REM Development setup script for Raspberry Pi Hardware Appliance (Windows)

echo Setting up development environment...

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install Python dependencies
pip install -r requirements-dev.txt

REM Create database
python -c "from app.models.database import db; print('Initializing database...'); db.init_db(); print('Database initialized successfully!')"

echo Development environment setup complete!
echo To run the application:
echo 1. Activate virtual environment: call venv\Scripts\activate
echo 2. Run the application: python run.py
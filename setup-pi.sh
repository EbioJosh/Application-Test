#!/bin/bash
# Raspberry Pi setup script for Hardware Appliance

echo "Setting up Raspberry Pi environment..."

# Update package list
sudo apt update

# Install system dependencies if needed
sudo apt install -y python3-venv python3-pip

# Create virtual environment
python3 -m venv rpi-venv

# Activate virtual environment
source rpi-venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Create database
python3 -c "
from app.models.database import db
print('Initializing database...')
db.init_db()
print('Database initialized successfully!')
"

echo "Raspberry Pi environment setup complete!"
echo "To run the application:"
echo "1. Activate virtual environment: source rpi-venv/bin/activate"
echo "2. Run the application: python3 run.py"
echo "3. Deactivate when done: deactivate"
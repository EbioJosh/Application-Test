#!/bin/bash
# Simple test script to run the application

echo "Starting Raspberry Pi 4B Test Environment..."

# Check if virtual environment exists
if [ ! -d "rpi-test-env" ]; then
    echo "Virtual environment not found. Running setup..."
    chmod +x setup-pi4b-test.sh
    ./setup-pi4b-test.sh
fi

# Activate virtual environment
echo "Activating virtual environment..."
source rpi-test-env/bin/activate

# Run the test application
echo "Starting application..."
echo "Access at: http://localhost:5000"
python test_app.py
#!/bin/bash
# Comprehensive troubleshooting script for Raspberry Pi 4B Test Environment

echo "=========================================="
echo "Troubleshooting Raspberry Pi 4B Test Environment"
echo "=========================================="

# Step 1: Check current directory
echo "1. Checking current directory..."
pwd
echo "Contents:"
ls -la
echo ""

# Step 2: Extract package if needed
if [ ! -d "pi4b-test-package" ]; then
    echo "2. Extracting rpi4b-hardware-test.zip..."
    if [ -f "rpi4b-hardware-test.zip" ]; then
        unzip rpi4b-hardware-test.zip
        echo "Extraction complete."
    else
        echo "ERROR: rpi4b-hardware-test.zip not found!"
        exit 1
    fi
else
    echo "2. pi4b-test-package already exists."
fi
echo ""

# Step 3: Change to package directory
echo "3. Changing to pi4b-test-package directory..."
cd pi4b-test-package
pwd
echo ""

# Step 4: Check contents
echo "4. Checking package contents..."
ls -la
echo ""

# Step 5: Run setup if virtual environment doesn't exist
if [ ! -d "rpi-test-env" ]; then
    echo "5. Virtual environment not found. Running setup..."
    if [ -f "setup-pi4b-test.sh" ]; then
        chmod +x setup-pi4b-test.sh
        ./setup-pi4b-test.sh
    else
        echo "ERROR: setup-pi4b-test.sh not found!"
        exit 1
    fi
else
    echo "5. Virtual environment already exists."
fi
echo ""

# Step 6: Check if virtual environment was created successfully
echo "6. Checking virtual environment..."
if [ -d "rpi-test-env" ]; then
    echo "Virtual environment exists:"
    ls -la rpi-test-env/
else
    echo "ERROR: Virtual environment was not created successfully!"
    exit 1
fi
echo ""

# Step 7: Test if we can activate the virtual environment
echo "7. Testing virtual environment activation..."
source rpi-test-env/bin/activate
echo "Virtual environment activated. Python location:"
which python
echo ""

# Step 8: Check if required files exist
echo "8. Checking required application files..."
if [ -f "test_app.py" ]; then
    echo "test_app.py found"
else
    echo "ERROR: test_app.py not found!"
    exit 1
fi

if [ -f "run_test.sh" ]; then
    echo "run_test.sh found"
else
    echo "WARNING: run_test.sh not found, creating it..."
    echo '#!/bin/bash' > run_test.sh
    echo 'source rpi-test-env/bin/activate' >> run_test.sh
    echo 'python test_app.py' >> run_test.sh
    chmod +x run_test.sh
    echo "run_test.sh created"
fi
echo ""

# Step 9: Test application syntax
echo "9. Testing application syntax..."
python -m py_compile test_app.py
if [ $? -eq 0 ]; then
    echo "Syntax check passed"
else
    echo "ERROR: Syntax check failed!"
    exit 1
fi
echo ""

# Step 10: Show how to run the application
echo "10. Setup complete!"
echo "=========================================="
echo "To run the application:"
echo "1. Make sure you're in the pi4b-test-package directory"
echo "2. Run one of these commands:"
echo "   ./run_test.sh"
echo "   OR"
echo "   source rpi-test-env/bin/activate && python test_app.py"
echo ""
echo "Then access the application at: http://localhost:5000"
echo "API endpoints:"
echo "  http://localhost:5000/api/status"
echo "  http://localhost:5000/api/logs"
echo ""
echo "To stop the application, press Ctrl+C"
echo "=========================================="
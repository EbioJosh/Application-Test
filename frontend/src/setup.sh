#!/bin/bash
# Setup script for Raspberry Pi Banking Terminal Frontend

echo "Setting up Raspberry Pi Banking Terminal Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null
then
    echo "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null
then
    echo "npm is not installed. Please install Node.js (which includes npm) first."
    exit 1
fi

# Install dependencies
echo "Installing frontend dependencies..."
npm install

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "Frontend dependencies installed successfully!"
    
    echo "To start the development server, run:"
    echo "  npm start"
    echo ""
    echo "To build for production, run:"
    echo "  npm run build"
    echo ""
    echo "To integrate with the Flask backend, run the build script:"
    echo "  ./build.sh"
else
    echo "Failed to install frontend dependencies."
    exit 1
fi
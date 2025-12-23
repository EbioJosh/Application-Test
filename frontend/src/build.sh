#!/bin/bash
# Build script to integrate React frontend with Flask backend

echo "Building React frontend for Raspberry Pi Banking Terminal..."

# Create build directory if it doesn't exist
mkdir -p ../app/static

# Build React app
npm run build

# Copy build files to Flask static directory
cp -r build/* ../app/static/

echo "Frontend build complete!"
echo "Files copied to ../app/static/"
echo "The Flask backend will now serve the React frontend."
#!/bin/bash
# Development setup script for Raspberry Pi Hardware Appliance

echo "Setting up development environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create database
python -c "
from app.models.database import db
print('Initializing database...')
db.init_db()
print('Database initialized successfully!')
"

echo "Development environment setup complete!"
echo "To run the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the application: python run.py"
#!/bin/bash

# Exit on error
set -e

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Setup database if needed
if [ ! -f "crews.db" ]; then
    echo "Setting up database..."
    # Add any database initialization commands here if needed
fi

echo "===================="
echo "Setup completed successfully!"
echo "To start the API server, run: ./run_api.sh"
echo "===================="

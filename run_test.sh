#!/bin/bash

# Exit on error
set -e

# Activate virtual environment
source venv/bin/activate

# Run the tests
echo "Running tests..."
python test_crewai.py
#!/bin/bash

# Exit on error
set -e

# Activate virtual environment
source venv/bin/activate

# Run the API server
echo "Starting API server..."
python -m uvicorn src.agent_creator.api.api:app --reload --host 0.0.0.0 --port 8000

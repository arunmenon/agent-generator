#!/bin/bash

# Exit on error
set -e

# Activate CrewAI virtual environment
source venv_crewai/bin/activate

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
else
    echo "Warning: .env file not found"
    # Set OpenAI API key - you'll need to replace this with your own key
    export OPENAI_API_KEY="your-api-key-here"
fi

# For debugging
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Run the API server
echo "Starting fixed API server on port 8000..."
python fixed_api.py
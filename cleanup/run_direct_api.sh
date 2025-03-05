#!/bin/bash

# Activate virtual environment
source venv_crewai/bin/activate

# Run the direct API on port 8001 (to avoid conflict with existing server)
echo "Starting direct test API server on port 8001"
python direct_api.py
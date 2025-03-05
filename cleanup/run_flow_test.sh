#!/bin/bash

# Activate virtual environment
source venv_crewai/bin/activate

# Run the simplified API test
echo "Starting flow route test API server on port 8000"
python flow_route_api_test.py
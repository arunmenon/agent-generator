#!/bin/bash

# Exit on error
set -e

# Check if pyenv is available and has Python 3.10-3.12 installed
if command -v pyenv >/dev/null 2>&1; then
    if [ -d "$HOME/.pyenv/versions/3.10.0" ]; then
        echo "Found Python 3.10.0 installed with pyenv. Will use it for the virtual environment."
        PYTHON_CMD="$HOME/.pyenv/versions/3.10.0/bin/python"
    elif [ -d "$HOME/.pyenv/versions/3.11.0" ]; then
        echo "Found Python 3.11.0 installed with pyenv. Will use it for the virtual environment."
        PYTHON_CMD="$HOME/.pyenv/versions/3.11.0/bin/python"
    elif [ -d "$HOME/.pyenv/versions/3.12.0" ]; then
        echo "Found Python 3.12.0 installed with pyenv. Will use it for the virtual environment."
        PYTHON_CMD="$HOME/.pyenv/versions/3.12.0/bin/python"
    else
        # Check system Python version
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
        PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
        
        if [[ $PYTHON_MAJOR == "3" ]] && [[ $PYTHON_MINOR -ge 10 ]] && [[ $PYTHON_MINOR -le 12 ]]; then
            echo "System Python $PYTHON_VERSION is compatible. Will use it for the virtual environment."
            PYTHON_CMD="python3"
        else
            echo "Error: crewAI requires Python 3.10-3.12"
            echo "Your system Python version: $PYTHON_VERSION"
            echo "Please install a compatible Python version with pyenv:"
            echo "  pyenv install 3.10.0"
            echo "  pyenv local 3.10.0"
            exit 1
        fi
    fi
else
    # Check system Python version
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
    PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
    
    if [[ $PYTHON_MAJOR == "3" ]] && [[ $PYTHON_MINOR -ge 10 ]] && [[ $PYTHON_MINOR -le 12 ]]; then
        echo "System Python $PYTHON_VERSION is compatible. Will use it for the virtual environment."
        PYTHON_CMD="python3"
    else
        echo "Error: crewAI requires Python 3.10-3.12"
        echo "Your system Python version: $PYTHON_VERSION"
        echo "Consider installing pyenv to manage multiple Python versions:"
        echo "  https://github.com/pyenv/pyenv#installation"
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv_crewai" ]; then
    echo "Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv_crewai
    
    # Wait a moment for the virtual environment to be fully created
    sleep 1
fi

# Check if the virtual environment was created correctly
if [ ! -f "venv_crewai/bin/activate" ]; then
    echo "Error: Virtual environment creation failed. The activation script is missing."
    exit 1
fi

# Activate virtual environment
source venv_crewai/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode if setup.py exists
if [ -f "setup.py" ]; then
    pip install -e .
else
    echo "Note: No setup.py found. Skipping development mode installation."
fi

# Setup database if needed
if [ ! -f "crews.db" ]; then
    echo "Setting up database..."
    # Add any database initialization commands here if needed
fi

echo "===================="
echo "Setup completed successfully!"
echo "To start the API server, run: ./run_api.sh"
echo "===================="
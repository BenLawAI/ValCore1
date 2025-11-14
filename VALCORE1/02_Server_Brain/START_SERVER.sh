#!/bin/bash
# VALCORE1 Server Brain Startup Script
# Run this on ATOM server to start the VALCORE1 server

set -e  # Exit on error

echo "==================================="
echo "   VALCORE1 SERVER BRAIN (ATOM)"
echo "==================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Install with: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
source venv/bin/activate

# Install/update requirements
echo "Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r setup/requirements_server.txt
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "WARNING: Ollama is not installed!"
    echo "Install with: ./setup/install_ollama.sh"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Ollama is running
if command -v ollama &> /dev/null; then
    if ! pgrep -x "ollama" > /dev/null; then
        echo "Starting Ollama service..."
        ollama serve &
        sleep 3
        echo ""
    fi

    # Check if required models are available
    echo "Checking Ollama models..."
    if ! ollama list | grep -q "qwen2.5:14b"; then
        echo "WARNING: qwen2.5:14b model not found!"
        echo "Pull with: ollama pull qwen2.5:14b"
        echo ""
    fi
fi

# Check GPU availability
if command -v nvidia-smi &> /dev/null; then
    echo "GPU Status:"
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader
    echo ""
else
    echo "WARNING: nvidia-smi not found. GPU may not be available."
    echo ""
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start VALCORE1 Server
echo "Starting VALCORE1 Server Brain..."
echo "Server will listen on http://0.0.0.0:5000"
echo "Press Ctrl+C to stop"
echo ""

python3 main_server.py

# Cleanup on exit
trap "echo ''; echo 'Shutting down VALCORE1 Server...'; deactivate" EXIT

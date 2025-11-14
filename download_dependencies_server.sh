#!/bin/bash

################################################################################
# VALCORE1 Server Dependency Download Script
# For ATOM server (Linux)
################################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALCORE_ROOT="$SCRIPT_DIR/VALCORE1"
SERVER_DIR="$VALCORE_ROOT/02_Server_Brain"
SERVER_REQUIREMENTS="$SERVER_DIR/setup/requirements_server.txt"
PYTHON_MIN_VERSION="3.10"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

print_header() {
    echo -e "\n${MAGENTA}================================================================================${NC}"
    echo -e "${MAGENTA}$1${NC}"
    echo -e "${MAGENTA}================================================================================${NC}\n"
}

print_status() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%H:%M:%S')

    case $level in
        SUCCESS)
            echo -e "${GREEN}[$timestamp] [SUCCESS] $message${NC}"
            ;;
        ERROR)
            echo -e "${RED}[$timestamp] [ERROR] $message${NC}"
            ;;
        WARNING)
            echo -e "${YELLOW}[$timestamp] [WARNING] $message${NC}"
            ;;
        INFO)
            echo -e "${CYAN}[$timestamp] [INFO] $message${NC}"
            ;;
        *)
            echo "[$timestamp] [INFO] $message"
            ;;
    esac
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

version_compare() {
    # Returns 0 if $1 >= $2
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

# ============================================================================
# MAIN CHECKS
# ============================================================================

check_prerequisites() {
    print_header "CHECKING PREREQUISITES"

    # Check if running on Linux
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_status ERROR "This script is for Linux servers. Use download_dependencies.ps1 for Windows."
        exit 1
    fi

    print_status INFO "OS: $(uname -s) $(uname -r)"
    print_status INFO "Machine: $(uname -m)"

    # Check internet connection
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        print_status SUCCESS "Internet connection OK"
    else
        print_status ERROR "No internet connection detected"
        exit 1
    fi

    # Check disk space (need at least 100GB for models)
    local free_space=$(df -BG "$SCRIPT_DIR" | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$free_space" -gt 100 ]; then
        print_status SUCCESS "Disk space: ${free_space}GB free"
    else
        print_status WARNING "Disk space: ${free_space}GB free (recommend 100GB+)"
    fi
}

check_python() {
    print_header "CHECKING PYTHON"

    if command_exists python3; then
        local python_version=$(python3 --version 2>&1 | awk '{print $2}')
        print_status INFO "Python $python_version detected"

        if version_compare "$python_version" "$PYTHON_MIN_VERSION"; then
            print_status SUCCESS "Python version OK (>= $PYTHON_MIN_VERSION)"
            return 0
        else
            print_status ERROR "Python version too old (need >= $PYTHON_MIN_VERSION)"
            return 1
        fi
    else
        print_status ERROR "Python 3 not found"
        print_status INFO "Install with: sudo apt install python3 python3-pip python3-venv"
        return 1
    fi
}

check_nvidia() {
    print_header "CHECKING NVIDIA GPU"

    if command_exists nvidia-smi; then
        print_status SUCCESS "nvidia-smi found"

        # Get GPU info
        local driver_version=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)
        print_status INFO "NVIDIA Driver: $driver_version"

        # Count GPUs
        local gpu_count=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)
        print_status INFO "GPUs detected: $gpu_count"

        # List GPUs
        nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader | while read line; do
            print_status INFO "  GPU: $line"
        done

        return 0
    else
        print_status ERROR "nvidia-smi not found"
        print_status INFO "Install NVIDIA drivers: https://docs.nvidia.com/datacenter/tesla/tesla-installation-notes/"
        return 1
    fi
}

check_ollama() {
    print_header "CHECKING OLLAMA"

    if command_exists ollama; then
        print_status SUCCESS "Ollama is installed"

        # Check if Ollama service is running
        if systemctl is-active --quiet ollama 2>/dev/null || pgrep -x ollama >/dev/null; then
            print_status SUCCESS "Ollama service is running"

            # List installed models
            print_status INFO "Installed models:"
            ollama list 2>/dev/null || print_status WARNING "Could not list models"
        else
            print_status WARNING "Ollama installed but not running"
            print_status INFO "Start with: ollama serve &"
        fi

        return 0
    else
        print_status WARNING "Ollama not installed"
        return 1
    fi
}

install_ollama() {
    print_header "INSTALLING OLLAMA"

    if command_exists ollama; then
        print_status INFO "Ollama already installed, skipping..."
        return 0
    fi

    print_status INFO "Installing Ollama..."

    if curl -fsSL https://ollama.ai/install.sh | sh; then
        print_status SUCCESS "Ollama installed successfully"

        # Start Ollama service
        print_status INFO "Starting Ollama service..."
        if command_exists systemctl; then
            sudo systemctl enable ollama
            sudo systemctl start ollama
            print_status SUCCESS "Ollama service started"
        else
            print_status INFO "Starting Ollama in background..."
            nohup ollama serve > /tmp/ollama.log 2>&1 &
        fi

        return 0
    else
        print_status ERROR "Ollama installation failed"
        return 1
    fi
}

download_ollama_models() {
    print_header "DOWNLOADING OLLAMA MODELS"

    # Required models
    local models=(
        "qwen2.5:14b"
        "qwen2.5:7b"
    )

    for model in "${models[@]}"; do
        print_status INFO "Checking model: $model"

        if ollama list 2>/dev/null | grep -q "$model"; then
            print_status SUCCESS "Model $model already installed"
        else
            print_status INFO "Downloading model: $model (this may take 10-30 minutes)"
            if ollama pull "$model"; then
                print_status SUCCESS "Model $model downloaded"
            else
                print_status ERROR "Failed to download model: $model"
            fi
        fi
    done
}

install_python_packages() {
    print_header "INSTALLING PYTHON PACKAGES"

    if [ ! -f "$SERVER_REQUIREMENTS" ]; then
        print_status ERROR "Requirements file not found: $SERVER_REQUIREMENTS"
        return 1
    fi

    # Count packages
    local total_packages=$(grep -v '^#' "$SERVER_REQUIREMENTS" | grep -v '^$' | wc -l)
    print_status INFO "Found $total_packages packages to install"

    # Upgrade pip
    print_status INFO "Upgrading pip..."
    python3 -m pip install --upgrade pip

    # Install packages
    print_status INFO "Installing packages from requirements..."
    if python3 -m pip install -r "$SERVER_REQUIREMENTS"; then
        print_status SUCCESS "Server packages installed successfully"
        return 0
    else
        print_status ERROR "Package installation failed"
        return 1
    fi
}

test_dependencies() {
    print_header "TESTING DEPENDENCIES"

    local tests=(
        "Python:python3 -c 'import sys; print(sys.version)'"
        "Flask:python3 -c 'import flask; print(flask.__version__)'"
        "Ollama:python3 -c 'import ollama; print(\"OK\")'"
        "FAISS:python3 -c 'import faiss; print(\"OK\")'"
        "Sentence-Transformers:python3 -c 'from sentence_transformers import SentenceTransformer; print(\"OK\")'"
        "Schedule:python3 -c 'import schedule; print(\"OK\")'"
    )

    local passed=0
    local failed=0

    for test in "${tests[@]}"; do
        local name="${test%%:*}"
        local command="${test#*:}"

        printf "%-30s" "$name... "

        if eval "$command" >/dev/null 2>&1; then
            echo -e "${GREEN}[OK]${NC}"
            ((passed++))
        else
            echo -e "${RED}[FAILED]${NC}"
            ((failed++))
        fi
    done

    echo ""
    if [ $failed -eq 0 ]; then
        print_status SUCCESS "All tests passed: $passed/${#tests[@]}"
        return 0
    else
        print_status WARNING "Tests passed: $passed/${#tests[@]}, Failed: $failed"
        return 1
    fi
}

save_report() {
    print_header "GENERATING DEPENDENCY REPORT"

    local report_file="$SCRIPT_DIR/logs/dependency_report_server_$(date +%Y%m%d_%H%M%S).txt"

    mkdir -p "$SCRIPT_DIR/logs"

    cat > "$report_file" <<EOF
VALCORE1 SERVER DEPENDENCY REPORT
Generated: $(date '+%Y-%m-%d %H:%M:%S')
=============================================================================

SYSTEM INFORMATION:
-------------------
OS: $(uname -s) $(uname -r) $(uname -m)
Hostname: $(hostname)
User: $(whoami)

PYTHON:
-------
$(python3 --version)
Location: $(which python3)

PIP:
----
$(pip3 --version)

CUDA/GPU:
---------
$(nvidia-smi --query-gpu=index,name,driver_version,memory.total --format=csv 2>/dev/null || echo "N/A")

OLLAMA:
-------
Version: $(ollama --version 2>/dev/null || echo "Not installed")
Models:
$(ollama list 2>/dev/null || echo "N/A")

INSTALLED PACKAGES:
-------------------
$(pip3 list)

=============================================================================
EOF

    print_status SUCCESS "Report saved: $report_file"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    cat << "EOF"

██╗   ██╗ █████╗ ██╗      ██████╗ ██████╗ ██████╗ ███████╗ ██╗
██║   ██║██╔══██╗██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝███║
██║   ██║███████║██║     ██║     ██║   ██║██████╔╝█████╗  ╚██║
╚██╗ ██╔╝██╔══██║██║     ██║     ██║   ██║██╔══██╗██╔══╝   ██║
 ╚████╔╝ ██║  ██║███████╗╚██████╗╚██████╔╝██║  ██║███████╗ ██║
  ╚═══╝  ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═╝

Server Dependency Installation Script v2.0 (Linux)

EOF

    local start_time=$(date +%s)

    # Run checks
    check_prerequisites
    check_python || exit 1
    check_nvidia || print_status WARNING "No NVIDIA GPU detected - continuing anyway"

    # Install Ollama
    check_ollama || install_ollama

    # Install Python packages
    install_python_packages

    # Download Ollama models
    download_ollama_models

    # Test everything
    test_dependencies

    # Generate report
    save_report

    # Summary
    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    local minutes=$((elapsed / 60))

    print_header "INSTALLATION COMPLETE"
    print_status SUCCESS "Server dependencies installed successfully!"
    print_status SUCCESS "Total time: ${minutes} minutes"

    echo -e "\n${CYAN}Next steps:${NC}"
    echo "1. Start Ollama: ollama serve"
    echo "2. Verify models: ollama list"
    echo "3. Start Flask server: python3 VALCORE1/02_Server_Brain/main_server.py"
}

# Run main
main

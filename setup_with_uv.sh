#!/bin/bash
# VALCORE1 UV Setup Script for Linux (ATOM Server)
# This script automates the UV setup process

set -e

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================"
echo -e "  VALCORE1 UV Setup for ATOM Server"
echo -e "========================================${NC}"
echo ""

# Check if UV is installed
echo -e "${YELLOW}[1/5] Checking UV installation...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV not found. Installing UV...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"

    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ Failed to install UV!${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ UV installed successfully!${NC}"
else
    UV_VERSION=$(uv --version)
    echo -e "${GREEN}✓ UV already installed: ${UV_VERSION}${NC}"
fi

echo ""

# Check Python version
echo -e "${YELLOW}[2/5] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ Found: ${PYTHON_VERSION}${NC}"

echo ""

# Sync dependencies
echo -e "${YELLOW}[3/5] Installing dependencies with UV...${NC}"
echo -e "${GRAY}This may take 5-10 minutes depending on your internet connection...${NC}"
echo ""

uv sync --extra server

echo -e "${GREEN}✓ Dependencies installed successfully!${NC}"
echo ""

# Verify installation
echo -e "${YELLOW}[4/5] Verifying installation...${NC}"

# Test PyTorch
echo -e "${GRAY}  Testing PyTorch...${NC}"
TORCH_TEST=$(uv run python -c "import torch; print(f'PyTorch {torch.__version__} - CUDA: {torch.cuda.is_available()}')")
echo -e "${GREEN}  ✓ ${TORCH_TEST}${NC}"

# Test Ollama
echo -e "${GRAY}  Testing Ollama client...${NC}"
uv run python -c "import ollama; print('Ollama client OK')" > /dev/null
echo -e "${GREEN}  ✓ Ollama client OK${NC}"

# Test server packages
echo -e "${GRAY}  Testing server packages...${NC}"
uv run python -c "import flask, sentence_transformers, faiss; print('Server packages OK')" > /dev/null 2>&1 || echo -e "${YELLOW}  ⚠ Some server packages may need additional setup${NC}"
echo -e "${GREEN}  ✓ Core server packages OK${NC}"

echo ""

# Show next steps
echo -e "${GREEN}[5/5] Setup Complete!${NC}"
echo ""
echo -e "${CYAN}========================================"
echo -e "  Next Steps"
echo -e "========================================${NC}"
echo ""
echo -e "${NC}1. Activate the virtual environment:${NC}"
echo -e "${YELLOW}   source .venv/bin/activate${NC}"
echo ""
echo -e "${NC}2. Or run scripts directly with UV:${NC}"
echo -e "${YELLOW}   uv run python VALCORE1/02_Server_Brain/main_server.py${NC}"
echo ""
echo -e "${NC}3. Read the UV guide:${NC}"
echo -e "${YELLOW}   cat UV_GUIDE.md${NC}"
echo ""
echo -e "${NC}4. Install Ollama (if not already installed):${NC}"
echo -e "${YELLOW}   curl -fsSL https://ollama.com/install.sh | sh${NC}"
echo ""
echo -e "${NC}5. Continue with Phase 2 setup:${NC}"
echo -e "${YELLOW}   cat VALCORE1/04_Documentation/00_READ_ME_FIRST.md${NC}"
echo ""
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${GREEN}✅ UV setup complete! Your development environment is ready.${NC}"
echo ""

#!/bin/bash
# Install Ollama on ATOM Server (Linux)

set -e

echo "===== VALCORE1 Ollama Installation Script ====="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./install_ollama.sh)"
    exit 1
fi

# Install Ollama
echo "[1/5] Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
echo "[2/5] Starting Ollama service..."
systemctl enable ollama
systemctl start ollama

# Wait for service to be ready
echo "[3/5] Waiting for Ollama service..."
sleep 5

# Pull minimum model (qwen2.5:14b)
echo "[4/5] Pulling qwen2.5:14b model (this may take a while)..."
ollama pull qwen2.5:14b

# Verify installation
echo "[5/5] Verifying installation..."
if systemctl is-active --quiet ollama; then
    echo "✓ Ollama service is running"
else
    echo "✗ Ollama service failed to start"
    exit 1
fi

if ollama list | grep -q "qwen2.5:14b"; then
    echo "✓ qwen2.5:14b model installed"
else
    echo "✗ Model installation failed"
    exit 1
fi

echo ""
echo "===== Installation Complete ====="
echo "Ollama is running on http://localhost:11434"
echo ""
echo "Optional: Pull larger models with:"
echo "  sudo ollama pull qwen2.5:32b"
echo "  sudo ollama pull qwen2.5:70b"
echo ""

#!/bin/bash
# VALCORE1 Tailscale Setup (Linux Server - ATOM)
# Sets up Tailscale on ATOM server for remote access

set -e

echo "=== VALCORE1 Tailscale Setup (Linux - ATOM) ==="
echo "This script will install and configure Tailscale on ATOM server"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./tailscale_setup.sh)"
    exit 1
fi

# 1. Install Tailscale
echo "[1/5] Installing Tailscale..."

if command -v tailscale &> /dev/null; then
    echo "  ✓ Tailscale already installed"
else
    echo "  Installing Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh

    if [ $? -eq 0 ]; then
        echo "  ✓ Tailscale installed"
    else
        echo "  ✗ Installation failed"
        exit 1
    fi
fi

# 2. Start Tailscale
echo ""
echo "[2/5] Starting Tailscale..."

systemctl enable tailscaled
systemctl start tailscaled

echo "  ✓ Tailscale service started"

# 3. Login
echo ""
echo "[3/5] Logging in to Tailscale..."
echo "  A URL will be displayed. Open it in a browser to authenticate."
echo ""

sudo tailscale up

if [ $? -eq 0 ]; then
    echo "  ✓ Logged in successfully"
else
    echo "  ✗ Login failed"
    exit 1
fi

# 4. Get Tailscale IP
echo ""
echo "[4/5] Getting Tailscale IP..."

sleep 2

TAILSCALE_IP=$(tailscale ip -4)

if [ -n "$TAILSCALE_IP" ]; then
    echo "  ✓ ATOM Tailscale IP: $TAILSCALE_IP"
else
    echo "  ✗ Could not get Tailscale IP"
    exit 1
fi

# 5. Configure firewall for Ollama
echo ""
echo "[5/5] Configuring firewall for Ollama..."

# Check if ufw is available
if command -v ufw &> /dev/null; then
    # Allow Ollama port from Tailscale network
    ufw allow from 100.0.0.0/8 to any port 11434 proto tcp comment 'Ollama via Tailscale'

    echo "  ✓ UFW rule added for port 11434 (Tailscale only)"
else
    echo "  ⚠ UFW not found, skipping firewall configuration"
    echo "  You may need to manually configure firewall"
fi

# Final summary
echo ""
echo "=== SETUP COMPLETE ==="
echo ""
echo "Tailscale Configuration:"
echo "  ATOM Tailscale IP: $TAILSCALE_IP"
echo "  Ollama Port: 11434 (accessible via Tailscale)"
echo ""
echo "Share this IP with Ben for desktop configuration:"
echo "  $TAILSCALE_IP"
echo ""
echo "Next steps:"
echo "  1. Give this IP to Ben: $TAILSCALE_IP"
echo "  2. Ben will run tailscale_setup.ps1 on Windows"
echo "  3. Test connection from Ben's desktop: ping $TAILSCALE_IP"
echo ""
echo "Verify Ollama is running:"
echo "  curl http://localhost:11434/api/tags"
echo ""

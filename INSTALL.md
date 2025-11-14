# VALCORE1 Installation Guide

## Prerequisites

- Python 3.10 or higher
- NVIDIA GPU with CUDA support (optional, for GPU acceleration)
- Ollama installed and running
- 8GB+ RAM recommended

## Installation Options

### Option 1: Full Installation (Recommended)

Install all dependencies including voice, automation, and development tools:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

### Option 2: Minimal Installation

Install only core dependencies for API server and LLM:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install minimal dependencies
pip install -r requirements-minimal.txt
```

### Option 3: Development Installation

For developers who want to contribute or modify the code:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install
```

## Dependency Security

All dependencies are pinned to specific versions for:
- **Reproducibility**: Same versions across all installations
- **Security**: Known, tested versions without vulnerabilities
- **Stability**: Avoid breaking changes from updates

### Updating Dependencies

To update a specific package:

```bash
# Update single package
pip install --upgrade <package-name>

# Regenerate requirements with new versions
pip freeze > requirements.txt
```

To update all packages (caution: may introduce breaking changes):

```bash
# Backup current requirements
cp requirements.txt requirements.txt.backup

# Update all packages
pip install --upgrade -r requirements.txt

# Test thoroughly before committing!
```

### Security Scanning

Scan for known vulnerabilities:

```bash
# Install safety (included in requirements-dev.txt)
pip install safety

# Check for vulnerabilities
safety check --file requirements.txt
```

## Ollama Setup

VALCORE1 requires Ollama for LLM inference:

```bash
# Install Ollama (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Pull required models
ollama pull qwen2.5:14b  # For server (large LLM)
ollama pull qwen2.5:7b   # For client fallback (small LLM)

# Verify Ollama is running
ollama list
```

## Configuration

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and configure:
   - API authentication tokens
   - CORS origins
   - Ollama URLs
   - Library paths

3. Review configuration files:
   - `VALCORE1/01_Client_Brain/config/`
   - `VALCORE1/02_Server_Brain/config/`

## Verification

Test your installation:

```bash
# Test server
cd VALCORE1/02_Server_Brain
python main_server.py

# In another terminal, test client
cd VALCORE1/01_Client_Brain
python main_client.py
```

## Platform-Specific Notes

### Linux
- Install system dependencies for PyAudio:
  ```bash
  sudo apt-get install portaudio19-dev python3-pyaudio
  ```

- For Tesseract OCR:
  ```bash
  sudo apt-get install tesseract-ocr
  ```

### macOS
- Install system dependencies:
  ```bash
  brew install portaudio tesseract
  ```

### Windows
- Install Visual C++ Build Tools for some packages
- PyAudio may require manual installation from wheels
- Some automation features require administrator privileges

## GPU Support

### NVIDIA GPU (CUDA)

For GPU-accelerated FAISS and PyTorch:

```bash
# Uninstall CPU versions
pip uninstall faiss-cpu torch

# Install GPU versions
pip install faiss-gpu torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### AMD GPU (ROCm)

Follow PyTorch ROCm installation guide for AMD GPUs.

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Ollama Connection Errors

```bash
# Check Ollama is running
curl http://localhost:11434/api/version

# Restart Ollama
systemctl restart ollama  # Linux
# or manually restart the application
```

### Permission Errors

Some automation features may require elevated permissions:
```bash
# Run with appropriate permissions
sudo python main_client.py  # Use cautiously!
```

## Next Steps

- Read `ENV_SETUP.md` for environment configuration
- Review `SECURITY.md` for security best practices
- Check `README.md` for usage instructions
- Run `scripts/setup_backup_cron.sh` to enable automated backups

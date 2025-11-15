# VALCORE1 UV Setup Guide

## What is UV?

UV is a modern, extremely fast Python package manager and project manager written in Rust. It's a replacement for pip, pip-tools, virtualenv, poetry, and more. UV is 10-100x faster than traditional tools.

**Key Benefits:**
- **Fast**: 10-100x faster than pip
- **Reliable**: Uses a lock file for reproducible installs
- **Simple**: One tool replaces many (pip, virtualenv, pip-tools, etc.)
- **Modern**: Uses pyproject.toml standard

## Installation Status

✅ UV is already installed and configured for this project!

**Installed Version:** `uv 0.8.17`

## Project Configuration

The project has been configured with:
- `pyproject.toml` - Project metadata and dependencies
- `uv.lock` - Lock file for reproducible installs
- `.python-version` - Python version specification (3.11)
- `.venv/` - Virtual environment (auto-created by UV)

## Quick Start

### Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

**Or use UV's run command (no activation needed):**
```bash
uv run python script.py
```

### Common UV Commands

#### Install/Sync Dependencies
```bash
# Install all core dependencies
uv sync

# Install with client dependencies (for Windows desktop)
uv sync --extra client

# Install with server dependencies (for ATOM server)
uv sync --extra server

# Install everything (client + server + dev tools)
uv sync --all-extras
```

#### Add New Dependencies
```bash
# Add a new package
uv add package-name

# Add to client extras
uv add --extra client package-name

# Add to dev dependencies
uv add --dev package-name
```

#### Remove Dependencies
```bash
uv remove package-name
```

#### Run Python Scripts
```bash
# Run with UV (automatically uses the virtual environment)
uv run python VALCORE1/01_Client_Brain/main_client.py
uv run python VALCORE1/02_Server_Brain/main_server.py

# Or use the installed scripts
uv run valcore1-client
uv run valcore1-server
```

#### Run Tests
```bash
uv run pytest
```

#### Update Dependencies
```bash
# Update all dependencies
uv lock --upgrade

# Update specific package
uv lock --upgrade-package package-name
```

#### List Installed Packages
```bash
uv pip list
```

#### Show Package Info
```bash
uv pip show package-name
```

## Dependency Groups

The project has organized dependencies into groups:

### Core Dependencies (Always Installed)
- PyTorch (with CUDA support)
- Ollama client
- Pydantic
- NumPy
- psutil, pynvml
- aiohttp, requests

### Client Extras (Windows Desktop)
Install with: `uv sync --extra client`

- faster-whisper (Speech-to-text)
- onnxruntime-gpu (TTS)
- sounddevice, pyaudio (Audio I/O)
- pyautogui (Desktop automation)
- pystray (System tray)
- pywin32 (Windows-specific)

### Server Extras (ATOM Server)
Install with: `uv sync --extra server`

- faiss-cpu (Vector database)
- sentence-transformers (Embeddings)
- Flask (Web framework)
- schedule (Task scheduling)

### Dev Extras (Development Tools)
Install with: `uv sync --extra dev` or `uv sync --all-extras`

- ipython, jupyter
- pytest
- black, flake8
- loguru

## Installation Instructions by Machine

### Desktop (Windows)
```powershell
# Install UV if not already installed
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Navigate to project directory
cd path\to\ValCore1

# Install core + client dependencies
uv sync --extra client

# Activate environment
.\.venv\Scripts\Activate.ps1

# Verify installation
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import faster_whisper; print('✓ Faster-Whisper installed')"
```

### Server (ATOM - Linux)
```bash
# Install UV if not already installed
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to project directory
cd /path/to/ValCore1

# Install core + server dependencies
uv sync --extra server

# Activate environment
source .venv/bin/activate

# Verify installation
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import faiss; print('✓ FAISS installed')"
```

## Migrating from Requirements.txt

The project originally used requirements.txt files. These have been migrated to pyproject.toml:

- `requirements.txt` → Core dependencies in pyproject.toml
- `01_Client_Brain/setup/requirements_client.txt` → `[project.optional-dependencies] client`
- `02_Server_Brain/setup/requirements_server.txt` → `[project.optional-dependencies] server`

**Note:** The old requirements.txt files are kept for reference but are no longer used.

## Special Packages (Manual Installation)

Some packages are commented out in pyproject.toml because they need special handling:

### 1. pvporcupine (Wake Word Detection)
```bash
# Requires Picovoice API key
uv add pvporcupine
```

### 2. kokoro-onnx (TTS)
```bash
# May not be on PyPI - install from source if needed
# This is commented out in pyproject.toml
```

### 3. resemblyzer (Speaker Verification)
```bash
# Dev version - may need to install from git
uv pip install git+https://github.com/resemble-ai/Resemblyzer.git
```

## Troubleshooting

### "Command not found: uv"
Install UV:
- **Windows:** `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
- **Linux/Mac:** `curl -LsSf https://astral.sh/uv/install.sh | sh`

### "No CUDA available"
This is expected if you don't have an NVIDIA GPU or CUDA drivers installed. PyTorch will fall back to CPU mode.

For GPU support:
1. Install NVIDIA CUDA Toolkit 12.1+
2. Install appropriate GPU drivers
3. Reinstall PyTorch with CUDA:
   ```bash
   uv pip install torch --index-url https://download.pytorch.org/whl/cu121
   ```

### "Package not found"
Some packages may not be available on PyPI. Check the package name or install from git:
```bash
uv pip install git+https://github.com/user/repo.git
```

### "Dependency resolution failed"
Try:
```bash
# Clear cache
uv cache clean

# Resync
uv sync --reinstall
```

## Performance Comparison

**Traditional pip install:**
```
pip install -r requirements.txt
Time: ~10-15 minutes
```

**UV install:**
```
uv sync
Time: ~2-3 minutes (with cache)
Time: ~6-8 minutes (without cache)
```

**UV is 3-5x faster!**

## Best Practices

1. **Always use `uv sync`** after pulling changes from git
2. **Commit uv.lock** to git for reproducible builds
3. **Use `uv run`** instead of activating the venv manually
4. **Keep pyproject.toml** clean and organized
5. **Use extras** to separate client/server dependencies

## Additional Resources

- UV Documentation: https://docs.astral.sh/uv/
- pyproject.toml spec: https://packaging.python.org/en/latest/specifications/pyproject-toml/
- UV GitHub: https://github.com/astral-sh/uv

## Summary

**✅ UV Setup Complete!**

Your VALCORE1 project is now configured to use UV for fast, reliable dependency management. Use `uv sync` to install dependencies and `uv run` to run scripts.

**Next Steps:**
1. Run `uv sync --extra client` (on Windows desktop)
2. Run `uv sync --extra server` (on ATOM server)
3. Follow the Phase 2 setup guide in `04_Documentation/00_READ_ME_FIRST.md`

---

**Questions?** Check the troubleshooting section above or consult the UV documentation.

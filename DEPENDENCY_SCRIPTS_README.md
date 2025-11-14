# VALCORE1 Dependency Management Scripts

## Overview

These scripts help you download, install, and verify all dependencies needed for VALCORE1.

---

## 📜 Available Scripts

### 1. `download_dependencies.ps1` (Windows - Client)

**Purpose:** Complete dependency download and installation for Windows desktop (client brain)

**What it does:**
- ✅ Checks Python installation and version
- ✅ Verifies NVIDIA drivers and CUDA
- ✅ Installs PyTorch with CUDA 12.1 support
- ✅ Installs all client Python packages
- ✅ Downloads Faster-Whisper models
- ✅ Tests all dependencies
- ✅ Generates detailed report

**Usage:**
```powershell
# Basic usage (installs everything)
.\download_dependencies.ps1

# Skip Python check
.\download_dependencies.ps1 -SkipPython

# Skip model downloads
.\download_dependencies.ps1 -SkipModels

# Force reinstall everything
.\download_dependencies.ps1 -Force

# Check only (no downloads)
.\download_dependencies.ps1 -Offline
```

**Estimated Time:** 15-30 minutes (depending on download speed)

**Downloads:** ~5-7 GB total

---

### 2. `download_dependencies_server.sh` (Linux - Server)

**Purpose:** Complete dependency download and installation for ATOM server

**What it does:**
- ✅ Checks Python installation and version
- ✅ Verifies NVIDIA drivers and CUDA
- ✅ Installs Ollama
- ✅ Downloads Qwen2.5:14b and Qwen2.5:7b models
- ✅ Installs all server Python packages
- ✅ Tests all dependencies
- ✅ Generates detailed report

**Usage:**
```bash
# Make executable
chmod +x download_dependencies_server.sh

# Run installation
./download_dependencies_server.sh
```

**Estimated Time:** 20-40 minutes (model downloads are large)

**Downloads:** ~15-20 GB total (Ollama models)

---

### 3. `check_dependencies.ps1` (Windows - Quick Check)

**Purpose:** Quick dependency verification (no downloads)

**What it does:**
- ✅ Checks all required dependencies
- ✅ Shows what's installed vs missing
- ✅ Provides installation commands for missing items
- ✅ Fast (completes in ~10 seconds)

**Usage:**
```powershell
# Quick check
.\check_dependencies.ps1

# Verbose output (shows details)
.\check_dependencies.ps1 -Verbose

# Export report to file
.\check_dependencies.ps1 -ExportReport
```

**When to use:**
- Before running VALCORE1
- After installing dependencies
- Troubleshooting setup issues
- Verifying environment

---

## 🚀 Quick Start Guide

### For Windows Desktop (Client)

**Step 1:** Check what's already installed
```powershell
.\check_dependencies.ps1 -Verbose
```

**Step 2:** Download missing dependencies
```powershell
.\download_dependencies.ps1
```

**Step 3:** Verify everything installed
```powershell
.\check_dependencies.ps1
```

**Step 4:** You're ready!
```powershell
python VALCORE1/01_Client_Brain/main_client.py
```

---

### For Linux Server (ATOM)

**Step 1:** Run installation script
```bash
chmod +x download_dependencies_server.sh
./download_dependencies_server.sh
```

**Step 2:** Verify Ollama
```bash
ollama list
```

**Step 3:** Start server
```bash
python3 VALCORE1/02_Server_Brain/main_server.py
```

---

## 📊 What Gets Installed

### Windows Client Dependencies

**Python Packages:**
- PyTorch 2.1.0+ (with CUDA 12.1)
- faster-whisper
- pyaudio / sounddevice
- pvporcupine (wake word)
- resemblyzer (speaker verification)
- onnxruntime (Kokoro TTS)
- pyautogui / pygetwindow (automation)
- requests (HTTP client)
- numpy, scipy
- pillow (screenshots)
- psutil (system monitoring)
- pynvml (GPU monitoring)
- keyboard (hotkeys)
- pystray (system tray)

**Models:**
- Faster-Whisper large-v3-turbo (~3 GB)

**Total Download Size:** ~5-7 GB

---

### Linux Server Dependencies

**Python Packages:**
- Flask / Flask-CORS (web server)
- ollama (Python client)
- faiss-cpu or faiss-gpu (vector search)
- sentence-transformers (embeddings)
- schedule (task scheduling)
- requests
- numpy

**Ollama Models:**
- qwen2.5:14b (~8 GB) - Main LLM
- qwen2.5:7b (~4 GB) - Fallback LLM

**Total Download Size:** ~15-20 GB

---

## 🔧 Troubleshooting

### Python not found

**Windows:**
```powershell
winget install Python.Python.3.11
```

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

---

### NVIDIA drivers not found

**Windows:**
1. Download from: https://www.nvidia.com/Download/index.aspx
2. Select your GPU model
3. Install with default options
4. Reboot

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install nvidia-driver-550

# Or use NVIDIA's official installer
wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda_12.1.0_530.30.02_linux.run
sudo sh cuda_12.1.0_530.30.02_linux.run
```

---

### PyTorch CUDA not available

**Check CUDA version:**
```powershell
nvidia-smi
```

**Reinstall PyTorch:**
```powershell
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Verify:**
```powershell
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

---

### Ollama models won't download

**Check Ollama service:**
```bash
# Check if running
pgrep ollama

# Start if not running
ollama serve &

# Download model manually
ollama pull qwen2.5:14b
```

**Check disk space:**
```bash
df -h
```

---

### PyAudio installation fails

**Windows:**
```powershell
# Download pre-built wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

# Then install:
pip install PyAudio‑0.2.11‑cp311‑cp311‑win_amd64.whl
```

**Linux:**
```bash
sudo apt install portaudio19-dev python3-pyaudio
pip3 install pyaudio
```

---

## 📈 Progress Tracking

All scripts generate detailed reports in the `logs/` directory:

**Report files:**
- `dependency_report_YYYYMMDD_HHMMSS.txt` (Windows)
- `dependency_report_server_YYYYMMDD_HHMMSS.txt` (Linux)

**Reports include:**
- System information
- Python version and packages
- GPU information
- CUDA version
- Installation status
- Full package list

---

## ⚡ Performance Tips

### Faster Downloads

**Use a download mirror:**
```powershell
# Set pip mirror (example: China)
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

**Parallel downloads:**
```powershell
# PyTorch supports multi-threaded downloads
$env:PIP_PARALLEL_DOWNLOAD="4"
```

### Resume Failed Downloads

All scripts are **idempotent** - you can run them multiple times:
- Already installed packages are skipped
- Downloaded models are not re-downloaded
- Only missing items are installed

**If a script fails halfway:**
```powershell
# Just run it again
.\download_dependencies.ps1

# It will skip what's already done and continue
```

---

## 🔐 Security Notes

### Verify Downloads

The scripts download from official sources:
- Python packages: pypi.org
- PyTorch: pytorch.org
- Ollama: ollama.ai
- Models: Hugging Face / official repos

### Firewall Permissions

Windows may prompt for firewall access:
- Python.exe (for network requests)
- nvidia-smi.exe (for GPU monitoring)

**Allow these** - they're needed for VALCORE1 to function.

---

## 📞 Getting Help

### Check Script Output

All scripts provide detailed status messages:
- 🟢 **[SUCCESS]** - Completed successfully
- 🟡 **[WARNING]** - Completed with warnings
- 🔴 **[ERROR]** - Failed (check message)
- 🔵 **[INFO]** - Information only

### Export Report

```powershell
# Windows
.\check_dependencies.ps1 -ExportReport

# Then share the .txt file when asking for help
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Python not found" | Install Python 3.10+ |
| "CUDA not available" | Update NVIDIA drivers |
| "Permission denied" | Run PowerShell as Administrator |
| "pip not found" | `python -m ensurepip --upgrade` |
| "Out of disk space" | Free up 50GB+ |
| "Download timeout" | Check internet connection |

---

## 🎯 Next Steps

After running the dependency scripts:

1. ✅ Review `SETUP_INSTRUCTIONS.md`
2. ✅ Get Picovoice access key
3. ✅ Configure `voice_config.json`
4. ✅ Run VALCORE1!

---

## 📝 Script Maintenance

### Updating Package Versions

Edit the requirements files:
- Client: `VALCORE1/01_Client_Brain/setup/requirements_client.txt`
- Server: `VALCORE1/02_Server_Brain/setup/requirements_server.txt`

Then run:
```powershell
.\download_dependencies.ps1 -Force
```

### Adding New Dependencies

1. Add to appropriate `requirements_*.txt`
2. Update `download_dependencies.ps1` or `.sh`
3. Update `check_dependencies.ps1`
4. Test on clean environment

---

**Created:** 2025-11-14
**Version:** 2.0
**Maintained by:** VALCORE1 Project

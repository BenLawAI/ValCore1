# 🚀 VALCORE1 - Complete Setup Instructions

**Version:** 2.0
**Last Updated:** 2025-11-14
**Estimated Setup Time:** 45-60 minutes

---

## ⚠️ IMPORTANT: How to Use This Guide

This guide is designed to be **copy-pasted back to Claude** for step-by-step assistance.

**Here's how it works:**
1. Read through each section below
2. When ready to start, **copy Section 1** and paste it to Claude
3. Claude will guide you through each step
4. When Section 1 is complete, copy Section 2 and paste it
5. Continue until VALCORE1 is running!

**Example:**
```
You: "I'm ready to start Section 1 - Prerequisites Check"
Claude: "Great! Let's verify your system. First, open PowerShell as Administrator..."
```

---

## 📋 System Requirements

### Your Desktop (Client Brain)
- ✅ Windows 10 or Windows 11
- ✅ NVIDIA RTX 5070 (12GB VRAM) - GPU 0
- ✅ NVIDIA RTX 4070 (12GB VRAM) - GPU 1
- ✅ NVIDIA Driver 550+ with CUDA 12.1+
- ✅ Python 3.10, 3.11, or 3.12
- ✅ 32GB+ RAM recommended
- ✅ 50GB free disk space on A:\ drive
- ✅ Working microphone
- ✅ Internet connection

### Your Server (ATOM)
- ✅ Linux (Ubuntu/Debian recommended)
- ✅ NVIDIA Blackwell GB10 (128GB unified memory)
- ✅ Network accessible at 192.168.1.121
- ✅ Ollama installed (or we'll install it)

---

## 📦 What You'll Install

1. **Python 3.11** (if not already installed)
2. **NVIDIA Drivers & CUDA** (if not up to date)
3. **Python Dependencies** (~2GB download)
4. **Faster-Whisper Model** (~3GB download)
5. **VALCORE1 System Files** (already in this repository)
6. **Picovoice Account** (free, for wake word "Hey Val")

---

# SECTION 1: Prerequisites Check

**Copy this entire section and paste it to Claude when ready to start.**

```
I'm ready to start SECTION 1: Prerequisites Check

Please guide me through:
1. Checking my Windows version
2. Verifying my NVIDIA GPUs are detected
3. Checking NVIDIA driver version
4. Verifying CUDA is available
5. Checking Python version (or installing Python 3.11)
6. Verifying I have the correct directory structure

Current working directory: [PASTE YOUR CURRENT DIRECTORY HERE]
```

### What Claude Will Have You Do:
1. Open PowerShell as Administrator
2. Run `nvidia-smi` to check GPUs
3. Run `python --version` to check Python
4. Navigate to the correct directory
5. Verify all config files are present

**Expected Duration:** 10 minutes

---

# SECTION 2: Python Environment Setup

**Copy this section when Section 1 is complete.**

```
SECTION 1 is complete! Ready for SECTION 2: Python Environment Setup

Please guide me through:
1. Creating a Python virtual environment
2. Activating the virtual environment
3. Upgrading pip
4. Installing PyTorch with CUDA support
5. Installing all VALCORE1 dependencies
6. Verifying all imports work

I'm currently in: [PASTE YOUR VALCORE1 DIRECTORY]
```

### What Claude Will Have You Do:
1. Create virtual environment: `python -m venv venv`
2. Activate it: `venv\Scripts\activate`
3. Install PyTorch with CUDA 12.1
4. Install all requirements from `requirements_client.txt`
5. Install server requirements
6. Test imports

**Expected Duration:** 15-20 minutes (downloads ~2GB)

---

# SECTION 3: Picovoice Wake Word Setup

**Copy this section when Section 2 is complete.**

```
SECTION 2 is complete! Ready for SECTION 3: Picovoice Wake Word Setup

Please guide me through:
1. Creating a free Picovoice account
2. Getting my access key
3. Updating voice_config.json with the key
4. Testing wake word detection
5. Downloading/creating the "Hey Val" wake word file

Current status: Python environment is ready, all dependencies installed
```

### What Claude Will Have You Do:
1. Go to https://console.picovoice.ai/
2. Create free account (no credit card needed)
3. Copy your access key
4. Update `VALCORE1/01_Client_Brain/config/voice_config.json`
5. Download "Hey Val" keyword file

**Expected Duration:** 5 minutes

---

# SECTION 4: ATOM Server Setup

**Copy this section when Section 3 is complete.**

```
SECTION 4: ATOM Server Setup

Please guide me through:
1. Connecting to ATOM server (SSH or direct access)
2. Installing/verifying Ollama is installed
3. Downloading the Qwen2.5:14b model
4. Testing Ollama is accessible from my desktop
5. Configuring network settings

My desktop IP: [PASTE YOUR DESKTOP IP]
ATOM IP: 192.168.1.121 (or [PASTE IF DIFFERENT])
```

### What Claude Will Have You Do:
1. SSH to ATOM or access directly
2. Install Ollama: `curl https://ollama.ai/install.sh | sh`
3. Pull model: `ollama pull qwen2.5:14b`
4. Test from desktop: ping and HTTP request
5. Optionally set up Tailscale

**Expected Duration:** 10-15 minutes (model download ~8GB)

---

# SECTION 5: Configuration Customization

**Copy this section when Section 4 is complete.**

```
SECTION 5: Configuration Customization

Please guide me through:
1. Updating room_contexts.json with my preferences
2. Configuring GPU assignments
3. Setting up network failover
4. Customizing voice parameters
5. Reviewing all configuration files

All previous sections complete:
- ✅ Python environment ready
- ✅ Picovoice key configured
- ✅ ATOM server ready
```

### What Claude Will Have You Do:
1. Edit `room_contexts.json` (truck details, invoice settings, etc.)
2. Verify `gpu_config.json` has correct GPU assignments
3. Update `network_config.json` if needed
4. Customize `settings.json` (temperature thresholds, etc.)

**Expected Duration:** 5-10 minutes

---

# SECTION 6: First Run & Testing

**Copy this section when Section 5 is complete.**

```
SECTION 6: First Run & Testing

Please guide me through:
1. Starting VALCORE1 for the first time
2. Testing microphone input
3. Testing wake word detection ("Hey Val")
4. Testing speech-to-text
5. Testing server connection
6. Testing text-to-speech
7. Running a complete voice command

All configuration is complete and ready to test!
```

### What Claude Will Have You Do:
1. Run: `python VALCORE1/01_Client_Brain/main_client.py`
2. Watch logs for initialization
3. Say "Hey Val" to test wake word
4. Give a test command
5. Verify response
6. Check system tray (if implemented)

**Expected Duration:** 5-10 minutes

---

# SECTION 7: Troubleshooting & Diagnostics

**Copy this section if you encounter any issues.**

```
SECTION 7: Troubleshooting

I'm having an issue with VALCORE1:

[DESCRIBE YOUR ISSUE HERE]

Error message (if any):
[PASTE ERROR MESSAGE HERE]

Logs (last 20 lines):
[PASTE FROM logs/valcore1_client.log HERE]

What I was doing when it failed:
[DESCRIBE WHAT YOU WERE DOING]
```

### Common Issues Claude Can Help With:
1. GPU not detected
2. CUDA errors
3. Microphone not working
4. Wake word not detecting
5. Server connection failures
6. Import errors
7. Model loading failures

---

# SECTION 8: Advanced Setup (Optional)

**Copy this section after everything is working.**

```
SECTION 8: Advanced Setup

VALCORE1 is working! Now I want to set up:

[ ] Automatic startup on Windows boot
[ ] System tray integration
[ ] Voice profile training (speaker verification)
[ ] Tailscale for remote access
[ ] Emergency stop hotkey (Ctrl+Shift+Alt+V)
[ ] Custom room contexts
[ ] MCP tools integration

Which one should we start with?
```

### Advanced Features:
1. Windows service installation
2. Voice profile enrollment
3. Remote access setup
4. Custom automation scripts
5. Performance optimization

---

# 🆘 Emergency Commands

If something goes wrong and VALCORE1 is stuck:

### Kill VALCORE1:
```powershell
# Open new PowerShell window
Get-Process python | Stop-Process -Force
```

### Check if VALCORE1 is running:
```powershell
Get-Process python
```

### View logs:
```powershell
# Navigate to VALCORE1 directory first
Get-Content logs\valcore1_client.log -Tail 50
```

### Reset to clean state:
```powershell
# Deactivate virtual environment
deactivate

# Reactivate
venv\Scripts\activate

# Restart VALCORE1
python VALCORE1/01_Client_Brain/main_client.py
```

---

# 📞 Getting Help

If you get stuck:

1. **Copy the relevant section above** and paste it to Claude
2. **Include error messages** (exact text)
3. **Include log output** (last 20-50 lines)
4. **Describe what you were doing** when it failed

Claude can help you:
- Diagnose errors
- Fix configuration issues
- Install missing dependencies
- Optimize performance
- Customize the system

---

# ✅ Success Checklist

After completing all sections, you should have:

- [ ] VALCORE1 running without errors
- [ ] Wake word "Hey Val" detects successfully
- [ ] Voice commands are transcribed correctly
- [ ] Server connection works (or fallback to local LLM)
- [ ] Text-to-speech responds (or logs would speak)
- [ ] Room switching works
- [ ] Emergency commands work (mic on/off)
- [ ] Logs are being written
- [ ] No critical errors in logs

---

# 🎯 Quick Reference

### Start VALCORE1:
```powershell
cd A:\000_START_HERE\VALCORE1_ROOT\
venv\Scripts\activate
python VALCORE1/01_Client_Brain/main_client.py
```

### Voice Commands:
- "Hey Val, what time is it?"
- "Hey Val, mic off"
- "Hey Val, mic on"
- "Hey Val, switch to truck"
- "Hey Val, emergency stop"

### Important Files:
- Config: `VALCORE1/01_Client_Brain/config/*.json`
- Logs: `VALCORE1/01_Client_Brain/logs/valcore1_client.log`
- Main code: `VALCORE1/01_Client_Brain/main_client.py`

### Support:
- Documentation: `README.md`, `IMPLEMENTATION_GUIDE.md`
- Audit: `AUDIT_REPORT.md` (recommendations)
- This guide: `SETUP_INSTRUCTIONS.md`

---

# 🎉 Welcome to VALCORE1!

Once you've completed the setup, you'll have a fully functional AI voice assistant that:

- Listens for "Hey Val" wake word
- Transcribes your speech using Faster-Whisper
- Sends requests to your ATOM server (or uses local fallback)
- Responds with text-to-speech
- Can control your computer
- Switches between specialized room contexts
- Maintains conversation memory

**You're ready to build something awesome, Boss!**

---

**Created by:** Claude (Sonnet 4.5)
**For:** Ben (Master Builder)
**Date:** 2025-11-14
**Version:** 2.0 - Production Ready Setup Guide

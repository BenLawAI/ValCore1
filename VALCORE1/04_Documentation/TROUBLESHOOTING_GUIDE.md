# VALCORE1 Troubleshooting Guide

**Version:** 1.0
**Last Updated:** 2025-11-14

---

## Table of Contents

1. [Setup Issues](#setup-issues)
2. [Voice System Problems](#voice-system-problems)
3. [Network & ATOM Issues](#network--atom-issues)
4. [LLM Response Issues](#llm-response-issues)
5. [GPU & Performance Issues](#gpu--performance-issues)
6. [Automation Issues](#automation-issues)
7. [System Crashes & Errors](#system-crashes--errors)
8. [Log Analysis](#log-analysis)

---

## Setup Issues

### Python Version Too Old

**Symptom:** Tests fail with "Python 3.10+ required"

**Solution:**
```powershell
# Download Python 3.10 or later from:
https://www.python.org/downloads/

# During install, check "Add Python to PATH"

# Verify:
python --version
```

### Missing Python Packages

**Symptom:** Import errors when running tests

**Solution:**
```powershell
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1

# Reinstall all dependencies
pip install -r requirements.txt

# Or install individually:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install faster-whisper sounddevice numpy requests pydantic flask
pip install pyautogui pystray pillow psutil pynvml
```

### Virtual Environment Issues

**Symptom:** "venv not found" or packages not installing

**Solution:**
```powershell
# Remove old venv
Remove-Item -Recurse -Force venv

# Recreate
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

### Administrator Privileges Required

**Symptom:** "Access denied" when running scripts

**Solution:**
- Right-click PowerShell
- Select "Run as Administrator"
- Navigate to script location
- Re-run script

---

## Voice System Problems

### Microphone Not Detected

**Symptom:** "No input devices found"

**Diagnosis:**
```powershell
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\05_Setup_Scripts\Diagnostic
.\3_test_microphone.ps1
```

**Solutions:**

1. **Check Windows Privacy:**
   - Settings > Privacy > Microphone
   - Enable "Allow apps to access your microphone"
   - Enable for Python

2. **Check Device Manager:**
   - Open Device Manager
   - Expand "Audio inputs and outputs"
   - Ensure microphone is enabled

3. **Reinstall Audio Driver:**
   - Device Manager > Microphone > Uninstall
   - Restart PC
   - Driver will auto-reinstall

4. **Test in Windows:**
   - Settings > System > Sound
   - Test microphone
   - Ensure it's set as default

### Wake Word Not Triggering

**Symptom:** Voice commands don't activate

**Solutions:**

1. **Check Wake Word Config:**
   ```powershell
   notepad A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\voice_config.json
   ```

   Verify `wake_word_model_path` points to valid .ppn file

2. **Re-train Wake Word:**
   ```powershell
   cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\05_Setup_Scripts\Voice_Enrollment
   .\1_record_wake_word.ps1
   ```

3. **Use Always-On Mode (Temporary):**
   Edit `voice_config.json`:
   ```json
   {
     "use_wake_word": false
   }
   ```

   ⚠️ **Warning:** This makes microphone always active

4. **Check Microphone Level:**
   - Recording level too low
   - Increase in Windows Sound settings
   - Aim for -12dB to -6dB when speaking

### Speech-to-Text Not Working

**Symptom:** No transcription or garbage text

**Diagnosis:**
```powershell
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\05_Setup_Scripts\Testing
.\2_test_voice_pipeline.ps1
```

**Solutions:**

1. **Check Faster-Whisper Installation:**
   ```powershell
   pip uninstall faster-whisper
   pip install faster-whisper
   ```

2. **Check GPU Memory:**
   ```powershell
   nvidia-smi
   ```

   If RTX 5070 is full, close other GPU apps

3. **Use CPU Mode (Temporary):**
   Edit `voice_config.json`:
   ```json
   {
     "stt_device": "cpu"
   }
   ```

4. **Download Model Manually:**
   ```python
   from faster_whisper import WhisperModel
   model = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
   ```

### Speaker Verification Failing

**Symptom:** "Speaker not verified" errors

**Diagnosis:**
```powershell
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\05_Setup_Scripts\Voice_Enrollment
.\4_test_voice_verification.ps1
```

**Solutions:**

1. **Check Similarity Threshold:**
   If scores are 0.55-0.65 (close):

   Edit `voice_config.json`:
   ```json
   {
     "speaker_similarity_threshold": 0.55
   }
   ```

2. **Re-record Voice Profile:**
   ```powershell
   .\2_record_voice_profile.ps1
   ```

   Tips:
   - Use same microphone position
   - Record in same environment
   - Speak naturally
   - Aim for 30+ samples

3. **Disable Verification (Temporary):**
   Edit `voice_config.json`:
   ```json
   {
     "enable_speaker_verification": false
   }
   ```

   ⚠️ **Warning:** Anyone can use VALCORE1

### TTS Not Playing Audio

**Symptom:** Text response shows but no voice

**Solutions:**

1. **Check Speakers:**
   - Test Windows sound
   - Ensure speakers not muted
   - Check system volume

2. **Check TTS Config:**
   ```powershell
   notepad A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\voice_config.json
   ```

   Verify Kokoro settings

3. **Test TTS Directly:**
   ```python
   import sounddevice as sd
   import numpy as np

   # Generate test tone
   sample_rate = 16000
   duration = 1
   frequency = 440
   t = np.linspace(0, duration, int(sample_rate * duration))
   audio = np.sin(2 * np.pi * frequency * t)

   sd.play(audio, sample_rate)
   sd.wait()
   ```

---

## Network & ATOM Issues

### Cannot Ping ATOM Server

**Symptom:** "Destination host unreachable"

**Solutions:**

1. **Verify ATOM is Powered On:**
   - Check physical server
   - Lights should be on

2. **Check IP Address:**
   ```powershell
   # Try pinging gateway first
   ping 192.168.1.1

   # Then ATOM
   ping 192.168.1.121
   ```

3. **Find ATOM's Actual IP:**
   - Log into router
   - Check DHCP leases
   - Look for ATOM hostname

4. **Update Network Config:**
   ```powershell
   notepad A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\network_config.json
   ```

   Update `atom_local_ip`

5. **Check Firewall on Both Systems:**
   ```powershell
   # Windows Firewall
   .\05_Setup_Scripts\Windows\3_setup_firewall.ps1
   ```

   ```bash
   # On ATOM (Linux)
   sudo ufw status
   sudo ufw allow from 192.168.1.0/24 to any port 11434
   ```

### Ollama Not Responding

**Symptom:** Connection timeout to port 11434

**Diagnosis:**
```powershell
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\05_Setup_Scripts\Diagnostic
.\4_test_network_atom.ps1
```

**Solutions:**

1. **Check Ollama Status (on ATOM):**
   ```bash
   ssh ben@192.168.1.121
   systemctl status ollama
   ```

   If not running:
   ```bash
   sudo systemctl start ollama
   ```

2. **Check Ollama Listening Address:**
   ```bash
   sudo systemctl cat ollama
   ```

   Should show:
   ```
   Environment="OLLAMA_HOST=0.0.0.0:11434"
   ```

3. **Test Ollama Locally (on ATOM):**
   ```bash
   curl http://localhost:11434/api/tags
   ```

   Should return JSON with models

4. **Test from Desktop:**
   ```powershell
   curl http://192.168.1.121:11434/api/tags
   ```

5. **Restart Ollama:**
   ```bash
   sudo systemctl restart ollama
   ```

### High Network Latency

**Symptom:** Slow responses, timeouts

**Diagnosis:**
```powershell
Test-Connection -ComputerName 192.168.1.121 -Count 10
```

**Solutions:**

1. **Check Network Load:**
   - Close bandwidth-heavy apps
   - Pause downloads
   - Check for network congestion

2. **Use Wired Connection:**
   - WiFi can be slow/unstable
   - Use Ethernet for both desktop and ATOM

3. **Switch to Tailscale:**
   Sometimes Tailscale is faster than local network:

   ```powershell
   notepad A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\network_config.json
   ```

   Set:
   ```json
   {
     "prefer_tailscale": true
   }
   ```

4. **Increase Timeout:**
   ```json
   {
     "timeout_seconds": 60,
     "max_retries": 5
   }
   ```

### Tailscale Connection Issues

**Symptom:** Cannot reach ATOM via Tailscale

**Solutions:**

1. **Check Tailscale Status:**
   ```powershell
   tailscale status
   ```

   Should show ATOM in list

2. **Ping Tailscale IP:**
   ```powershell
   ping 100.x.x.x  # ATOM's Tailscale IP
   ```

3. **Restart Tailscale:**
   ```powershell
   tailscale down
   tailscale up
   ```

   ```bash
   # On ATOM
   sudo tailscale down
   sudo tailscale up
   ```

4. **Check Firewall:**
   Tailscale should auto-configure, but verify:

   ```bash
   # On ATOM
   sudo ufw allow from 100.0.0.0/8 to any port 11434
   ```

---

## LLM Response Issues

### No Response from LLM

**Symptom:** Request sent, no response

**Solutions:**

1. **Check ATOM GPU:**
   ```bash
   ssh ben@192.168.1.121
   nvidia-smi
   ```

   Look for:
   - GPU utilization (should be >0% when processing)
   - Memory usage
   - Temperature

2. **Check Model is Loaded:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

   Should list qwen2.5:14b or qwen2.5:70b

3. **Test Model Directly:**
   ```bash
   curl http://localhost:11434/api/generate -d '{
     "model": "qwen2.5:14b",
     "prompt": "Say test",
     "stream": false
   }'
   ```

4. **Check Logs:**
   ```bash
   sudo journalctl -u ollama -f
   ```

### Slow LLM Responses

**Symptom:** Responses take 30+ seconds

**Solutions:**

1. **Check Model Size:**
   70B model is slow on single GPU:

   ```json
   {
     "default_model": "qwen2.5:14b"
   }
   ```

2. **Check GPU Temperature:**
   ```bash
   nvidia-smi
   ```

   If >85°C, GPU may be throttling:
   - Clean dust from server
   - Check fan operation
   - Improve airflow

3. **Check System RAM:**
   ```bash
   free -h
   ```

   If low memory:
   - Close other apps on ATOM
   - Use smaller model
   - Add swap space

4. **Reduce Context Length:**
   Edit room configs:
   ```json
   {
     "max_tokens": 500
   }
   ```

### Garbled or Incorrect Responses

**Symptom:** LLM gives nonsense answers

**Solutions:**

1. **Check Temperature Setting:**
   Too high = random:

   ```json
   {
     "temperature": 0.7
   }
   ```

2. **Verify System Prompt:**
   ```powershell
   notepad A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\room_contexts.json
   ```

   Ensure prompts are clear

3. **Check Context Length:**
   If too much context:
   - Clear conversation history
   - Reduce librarian search results

4. **Try Different Model:**
   ```bash
   ollama pull qwen2.5:7b
   ```

   Smaller models sometimes more reliable

---

## GPU & Performance Issues

### GPU Not Detected

**Symptom:** CUDA tests fail

**Diagnosis:**
```powershell
nvidia-smi
```

**Solutions:**

1. **Update NVIDIA Drivers:**
   - Download from: https://www.nvidia.com/drivers
   - Install latest Game Ready or Studio driver
   - Restart PC

2. **Check GPU Power:**
   - Ensure PCIe power cables connected
   - Check GPU fans spinning
   - Verify GPU seated properly

3. **Check CUDA Installation:**
   ```powershell
   cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\05_Setup_Scripts\Diagnostic
   .\2_test_cuda.ps1
   ```

4. **Reinstall PyTorch with CUDA:**
   ```powershell
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

### GPU Memory Full

**Symptom:** "Out of memory" errors

**Diagnosis:**
```powershell
nvidia-smi
```

**Solutions:**

1. **Close Other GPU Apps:**
   - Games
   - Video editors
   - Browsers with hardware acceleration

2. **Use Smaller Models:**
   For Whisper:
   ```json
   {
     "stt_model": "medium"
   }
   ```

3. **Enable CPU Fallback:**
   ```json
   {
     "fallback_to_cpu_on_oom": true
   }
   ```

4. **Restart VALCORE1:**
   Sometimes memory leaks accumulate

### Wrong GPU Being Used

**Symptom:** Voice system using RTX 4070 instead of RTX 5070

**Solutions:**

1. **Check GPU Config:**
   ```powershell
   notepad A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\gpu_config.json
   ```

   Verify:
   ```json
   {
     "voice_device_id": 0,
     "fallback_llm_device_id": 1
   }
   ```

2. **Verify GPU Order:**
   ```powershell
   nvidia-smi -L
   ```

   Should show:
   - GPU 0: RTX 5070
   - GPU 1: RTX 4070

   If reversed, swap device_id values

---

## Automation Issues

### Automation Not Working

**Symptom:** Commands don't control desktop

**Solutions:**

1. **Check PyAutoGUI:**
   ```powershell
   pip install pyautogui
   ```

2. **Test Manually:**
   ```python
   import pyautogui
   pyautogui.write("test")
   ```

3. **Check Safety Features:**
   Won't type in terminal windows (by design)

4. **Enable Automation:**
   ```powershell
   notepad A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\automation_config.json
   ```

   Verify:
   ```json
   {
     "enabled": true
   }
   ```

### Automation Undo Not Working

**Symptom:** Can't undo automation actions

**Solution:**

Use emergency stop: **Ctrl+Shift+Alt+V**

This reverts last 3 actions

---

## System Crashes & Errors

### VALCORE1 Crashes on Startup

**Check logs:**
```powershell
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\logs
notepad client_brain.log
```

**Common causes:**

1. **Missing Config Files:**
   Re-run setup scripts

2. **Port Already in Use:**
   Another app using port 5000:
   ```powershell
   netstat -ano | findstr :5000
   ```

   Kill the process or change port in config

3. **Import Errors:**
   ```powershell
   pip install -r requirements.txt
   ```

### System Tray Icon Missing

**Solutions:**

1. **Check pystray:**
   ```powershell
   pip install pystray pillow
   ```

2. **Run Manually:**
   ```powershell
   cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\core
   python system_tray.py
   ```

3. **Check Windows Notification Area:**
   - Settings > Personalization > Taskbar
   - "Select which icons appear on taskbar"
   - Enable VALCORE1

### Flask Server Won't Start

**Symptom:** "Address already in use"

**Solutions:**

```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill it (replace PID)
taskkill /PID <PID> /F

# Or change port
notepad A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\02_Server_Brain\config\server_config.json
```

---

## Log Analysis

### Where Are the Logs?

```
A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\logs\
├── client_brain.log          - Desktop client
├── server_brain.log           - ATOM server (if using)
├── voice_system.log           - Voice processing
├── automation.log             - Desktop automation
├── health_metrics.csv         - System health
└── performance_metrics.csv    - Performance data
```

### Reading Error Messages

**Format:**
```
[TIMESTAMP] [LEVEL] [MODULE] Message
```

**Levels:**
- DEBUG: Verbose info (ignore unless debugging)
- INFO: Normal operation
- WARNING: Something odd but not critical
- ERROR: Something failed
- CRITICAL: System cannot continue

### Common Error Messages:

**"Connection refused"**
→ ATOM server not reachable
→ Check network and Ollama

**"CUDA out of memory"**
→ GPU memory full
→ Close other GPU apps or use smaller model

**"No module named 'X'"**
→ Package not installed
→ `pip install X`

**"Permission denied"**
→ Need administrator
→ Run PowerShell as admin

**"Timeout waiting for response"**
→ Network issue or LLM too slow
→ Check ATOM, increase timeout

---

## Getting More Help

### 1. Run Diagnostics:
```powershell
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\05_Setup_Scripts\Testing
.\RUN_ALL_TESTS.ps1
```

### 2. Check Recent Logs:
```powershell
cd ..\logs
Get-Content client_brain.log -Tail 50
```

### 3. Ask Val:
"Val, I'm getting error: [paste error message]"

### 4. Claude CLI Validation:
```bash
claude code validate-valcore1
```

---

## Emergency Procedures

### Complete Reset:

```powershell
# Stop all processes
Stop-Process -Name python -Force

# Remove virtual environment
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1
Remove-Item -Recurse -Force venv

# Reinstall
.\START_VALCORE1.bat

# Reconfigure
cd .\05_Setup_Scripts\Windows
.\3_setup_firewall.ps1
.\4_setup_audio_devices.ps1
```

### Backup Configuration:

```powershell
# Before making changes
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config
Copy-Item *.json A:\BACKUPS\valcore1_config_$(Get-Date -Format 'yyyyMMdd')\
```

---

**Still stuck?**

1. Check logs in `logs/` directory
2. Run full diagnostic suite
3. Ask Val for help with specific error
4. Use Claude CLI for validation

Most issues can be resolved by:
- Verifying network connectivity
- Ensuring all packages installed
- Checking GPU availability
- Reviewing configuration files

---

*VALCORE1 Troubleshooting Guide*
*Updated: November 2025*

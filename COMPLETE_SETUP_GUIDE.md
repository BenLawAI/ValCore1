# VALCORE1 - Complete Setup Guide for Ben

**Last Updated:** 2025-11-15
**Estimated Time:** 2-3 hours
**Difficulty:** Beginner-friendly (copy-paste commands)

This guide will walk you through:
1. Downloading VALCORE1 from GitHub
2. Installing it on your Windows desktop
3. Installing it on your ATOM server
4. Backing up to Google Drive
5. Running your first test

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Part 1: Download from GitHub](#part-1-download-from-github)
3. [Part 2: Install on Windows Desktop](#part-2-install-on-windows-desktop)
4. [Part 3: Install on ATOM Server](#part-3-install-on-atom-server)
5. [Part 4: Backup to Google Drive](#part-4-backup-to-google-drive)
6. [Part 5: First Test Run](#part-5-first-test-run)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You Need on Windows Desktop:
- [x] Windows 10 or 11
- [x] NVIDIA RTX 5070 and RTX 4070 installed
- [x] Internet connection
- [x] About 10 GB of free disk space
- [x] Administrator access

### What You Need on ATOM Server:
- [x] Linux (Ubuntu/Debian)
- [x] NVIDIA Blackwell GB10 GPU
- [x] Internet connection
- [x] About 20 GB of free disk space
- [x] SSH access

### Optional (Recommended):
- [ ] Google Drive Desktop app installed
- [ ] GitHub account (free)
- [ ] Tailscale account (for remote access)

---

## Part 1: Download from GitHub

### Option A: Download as ZIP (Easiest)

1. **Go to the GitHub repository:**
   - Open your web browser
   - Go to: `https://github.com/BenLawAI/ValCore1`

2. **Download the code:**
   - Click the green **"Code"** button
   - Click **"Download ZIP"**
   - Save it to your Downloads folder

3. **Extract the ZIP file:**
   - Right-click the downloaded ZIP file
   - Select **"Extract All..."**
   - Choose a location (recommended: `C:\VALCORE1\`)
   - Click **"Extract"**

### Option B: Clone with Git (Advanced)

If you have Git installed:

1. **Open PowerShell as Administrator:**
   - Press `Windows + X`
   - Click **"Windows PowerShell (Admin)"**

2. **Navigate to where you want to install:**
   ```powershell
   cd C:\
   ```

3. **Clone the repository:**
   ```powershell
   git clone https://github.com/BenLawAI/ValCore1.git
   cd ValCore1
   ```

4. **Switch to the latest branch:**
   ```powershell
   git checkout claude/audit-files-verification-01Sf2ttgw6x9xqQNtYvGn84n
   ```

---

## Part 2: Install on Windows Desktop

### Step 1: Install UV (Package Manager)

1. **Open PowerShell as Administrator:**
   - Press `Windows + X`
   - Click **"Windows PowerShell (Admin)"**

2. **Install UV:**
   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Wait for installation to complete** (should take 30-60 seconds)

4. **Verify UV is installed:**
   ```powershell
   uv --version
   ```
   - You should see something like: `uv 0.8.17`

### Step 2: Run Automated Setup

1. **Navigate to your VALCORE1 folder:**
   ```powershell
   cd C:\VALCORE1
   ```
   *(Adjust the path if you extracted it somewhere else)*

2. **Run the automated setup script:**
   ```powershell
   .\setup_with_uv.ps1
   ```

3. **What will happen:**
   - UV will check your Python installation
   - It will download and install 75+ packages (takes 5-10 minutes)
   - PyTorch with CUDA support will be installed
   - All voice processing libraries will be installed
   - You'll see green checkmarks ✓ as each step completes

4. **Wait for completion:**
   - You'll see a message: **"✅ UV setup complete!"**

### Step 3: Install NVIDIA Drivers (If Not Already Installed)

1. **Check if CUDA is installed:**
   ```powershell
   nvidia-smi
   ```

2. **If you see an error**, install NVIDIA drivers:
   - Go to: https://www.nvidia.com/Download/index.aspx
   - Select your GPU: RTX 5070
   - Download and install the driver
   - Restart your computer

3. **Install CUDA Toolkit:**
   - Go to: https://developer.nvidia.com/cuda-downloads
   - Download CUDA 12.1 or newer
   - Run the installer
   - Accept defaults
   - Restart your computer

### Step 4: Get Picovoice API Key

1. **Sign up for Picovoice (Free):**
   - Go to: https://console.picovoice.ai/signup
   - Create a free account
   - Verify your email

2. **Get your Access Key:**
   - Log in to: https://console.picovoice.ai/
   - Copy your **Access Key** (looks like: `ABC123xyz...`)

3. **Update the config file:**
   - Open: `C:\VALCORE1\VALCORE1\01_Client_Brain\config\voice_config.json`
   - Find the line: `"access_key": "YOUR_ACCESS_KEY_HERE"`
   - Replace `YOUR_ACCESS_KEY_HERE` with your actual key
   - Save the file

### Step 5: Test Your Installation

1. **Run the diagnostic tests:**
   ```powershell
   cd C:\VALCORE1
   .\VALCORE1\05_Setup_Scripts\Testing\1_test_full_system.ps1
   ```

2. **Check the results:**
   - Green ✓ = Working
   - Yellow ⚠ = Warning (may still work)
   - Red ❌ = Problem (needs fixing)

---

## Part 3: Install on ATOM Server

### Step 1: Transfer Files to ATOM

**Option A: Using SCP (Recommended)**

From your Windows desktop:

1. **Open PowerShell:**
   ```powershell
   cd C:\VALCORE1
   ```

2. **Copy to ATOM:**
   ```powershell
   scp -r . ben@192.168.1.121:~/ValCore1/
   ```
   *(Replace `ben` with your username and `192.168.1.121` with ATOM's IP)*

**Option B: Using USB Drive**

1. Copy `C:\VALCORE1\` to a USB drive
2. Plug USB into ATOM server
3. Copy from USB to ATOM's home directory

### Step 2: Install on ATOM

1. **SSH into ATOM:**
   ```bash
   ssh ben@192.168.1.121
   ```

2. **Navigate to VALCORE1:**
   ```bash
   cd ~/ValCore1
   ```

3. **Install UV:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

4. **Add UV to PATH** (for current session):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

5. **Run automated setup:**
   ```bash
   ./setup_with_uv.sh
   ```

6. **Wait for completion** (5-10 minutes)

### Step 3: Install Ollama (LLM Server)

1. **Install Ollama:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Start Ollama:**
   ```bash
   ollama serve &
   ```

3. **Download your preferred model:**
   ```bash
   # For 14B model (recommended):
   ollama pull qwen2.5:14b

   # For 70B model (if you have enough RAM):
   ollama pull qwen2.5:70b
   ```

4. **Test Ollama:**
   ```bash
   ollama run qwen2.5:14b "Hello, how are you?"
   ```
   - You should get a response back

### Step 4: Configure Network Access

1. **Edit ATOM's IP in client config:**
   - On Windows, open: `C:\VALCORE1\VALCORE1\01_Client_Brain\config\network_config.json`
   - Update the `atom_server_url` to your ATOM's IP:
   ```json
   {
     "atom_server_url": "http://192.168.1.121:5000",
     "ollama_url": "http://192.168.1.121:11434"
   }
   ```
   - Save the file

2. **Allow firewall access on ATOM:**
   ```bash
   sudo ufw allow 5000
   sudo ufw allow 11434
   ```

---

## Part 4: Backup to Google Drive

### Option A: Using Google Drive Desktop App (Easiest)

1. **Install Google Drive Desktop:**
   - Download from: https://www.google.com/drive/download/
   - Install and sign in with your Google account

2. **Set up syncing:**
   - Open Google Drive app
   - Click settings (gear icon)
   - Click **"Preferences"**
   - Go to **"My Computer"** tab
   - Click **"Add Folder"**
   - Select `C:\VALCORE1\`
   - Choose **"Sync with Google Drive"**
   - Click **"Done"**

3. **Wait for initial sync:**
   - This may take 30-60 minutes for the first backup
   - You'll see a green checkmark when complete

### Option B: Manual Backup to Google Drive

1. **Open Google Drive in browser:**
   - Go to: https://drive.google.com

2. **Create a folder:**
   - Click **"New"** → **"Folder"**
   - Name it: `VALCORE1_Backup`
   - Click **"Create"**

3. **Upload your VALCORE1 folder:**
   - Click **"New"** → **"Folder upload"**
   - Select `C:\VALCORE1\`
   - Click **"Upload"**
   - Wait for upload (30-60 minutes)

### Option C: Using Command Line (Advanced)

Using `rclone`:

1. **Install rclone:**
   ```powershell
   # Download from: https://rclone.org/downloads/
   ```

2. **Configure Google Drive:**
   ```powershell
   rclone config
   ```
   - Follow the prompts to set up Google Drive

3. **Sync to Drive:**
   ```powershell
   rclone sync C:\VALCORE1 gdrive:VALCORE1_Backup
   ```

### Recommended Backup Strategy

**For Safety:**
1. Keep a copy on Google Drive (cloud backup)
2. Keep a copy on an external USB drive (local backup)
3. Keep the original on your PC (active version)

**Backup Schedule:**
- Daily: Configuration files only
- Weekly: Full system backup
- Before major changes: Full backup

---

## Part 5: First Test Run

### On ATOM Server:

1. **SSH into ATOM:**
   ```bash
   ssh ben@192.168.1.121
   cd ~/ValCore1
   ```

2. **Start the server:**
   ```bash
   source .venv/bin/activate
   python VALCORE1/02_Server_Brain/main_server.py
   ```

   Or with UV:
   ```bash
   uv run python VALCORE1/02_Server_Brain/main_server.py
   ```

3. **You should see:**
   ```
   ========================================
   VALCORE1 Server Brain Starting...
   ========================================
   ✓ GPU detected: NVIDIA Blackwell GB10
   ✓ Ollama connected
   ✓ Vector database loaded
   ✓ Server listening on 0.0.0.0:5000
   ```

### On Windows Desktop:

1. **Open PowerShell:**
   ```powershell
   cd C:\VALCORE1
   ```

2. **Activate environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. **Start the client:**
   ```powershell
   python VALCORE1\01_Client_Brain\main_client.py
   ```

   Or with UV:
   ```powershell
   uv run python VALCORE1\01_Client_Brain\main_client.py
   ```

4. **You should see:**
   ```
   ========================================
   VALCORE1 Client Brain Starting...
   ========================================
   ✓ GPU 0 (RTX 5070) detected
   ✓ GPU 1 (RTX 4070) detected
   ✓ Microphone initialized
   ✓ Connected to ATOM server
   ✓ Wake word system ready

   Listening for "Hey Val"...
   ```

5. **Test it out:**
   - Say: **"Hey Val"**
   - Wait for the beep
   - Say: **"What time is it?"**
   - Val should respond!

---

## Troubleshooting

### Problem: "uv: command not found"

**Solution:**
```powershell
# Close and reopen PowerShell as Administrator
# Then verify:
uv --version

# If still not found, add to PATH manually:
$env:Path += ";$env:USERPROFILE\.local\bin"
```

### Problem: "CUDA not available"

**Solution:**
1. Run this command:
   ```powershell
   nvidia-smi
   ```
2. If it fails, reinstall NVIDIA drivers
3. If it works, run:
   ```powershell
   uv run python -c "import torch; print(torch.cuda.is_available())"
   ```
4. If it says `False`, reinstall PyTorch:
   ```powershell
   uv pip install torch --index-url https://download.pytorch.org/whl/cu121
   ```

### Problem: "Cannot connect to ATOM server"

**Solution:**
1. Check ATOM is running:
   ```bash
   ssh ben@192.168.1.121
   ps aux | grep main_server
   ```

2. Check firewall:
   ```bash
   sudo ufw status
   # Should show: 5000 ALLOW
   ```

3. Test connection from Windows:
   ```powershell
   curl http://192.168.1.121:5000/health
   ```

4. Check IP address in config:
   - Open: `VALCORE1\01_Client_Brain\config\network_config.json`
   - Verify the IP matches your ATOM server

### Problem: "Microphone not detected"

**Solution:**
1. Run the microphone test:
   ```powershell
   .\VALCORE1\05_Setup_Scripts\Diagnostic\3_test_microphone.ps1
   ```

2. Check Windows sound settings:
   - Right-click speaker icon in taskbar
   - Click "Sounds"
   - Go to "Recording" tab
   - Make sure your microphone is enabled and set as default

3. Update audio drivers

### Problem: "Wake word not working"

**Solution:**
1. Verify you added your Picovoice access key:
   - Check: `VALCORE1\01_Client_Brain\config\voice_config.json`
   - Should NOT say `YOUR_ACCESS_KEY_HERE`

2. Test wake word specifically:
   ```powershell
   .\VALCORE1\05_Setup_Scripts\Voice_Enrollment\1_record_wake_word.ps1
   ```

3. Speak clearly and close to the microphone

### Problem: "Out of memory" error

**Solution:**
1. Check GPU memory:
   ```powershell
   nvidia-smi
   ```

2. Try smaller models:
   - Edit: `VALCORE1\01_Client_Brain\config\settings.json`
   - Change `faster-whisper` model from `large-v3` to `medium` or `small`

3. Close other GPU applications

### Problem: Google Drive upload is slow

**Solution:**
1. Exclude the `.venv` folder from backup (it's large and can be recreated):
   - Right-click `.venv` folder
   - Select "Make available offline" → Uncheck

2. Upload during off-peak hours

3. Consider uploading only essential folders:
   - `VALCORE1/` (code)
   - `Library/` (memories)
   - Configuration files

---

## Quick Reference Card

### Start VALCORE1:

**ATOM Server:**
```bash
ssh ben@192.168.1.121
cd ~/ValCore1
uv run python VALCORE1/02_Server_Brain/main_server.py
```

**Windows Desktop:**
```powershell
cd C:\VALCORE1
uv run python VALCORE1\01_Client_Brain\main_client.py
```

### Stop VALCORE1:

- Press `Ctrl+C` in the terminal window
- Or say: **"Hey Val, stop listening"**
- Emergency stop: `Ctrl+Shift+Alt+V`

### Backup to Google Drive:

```powershell
# If using Google Drive Desktop, it auto-syncs
# If manual, upload C:\VALCORE1 to Drive
```

### Update VALCORE1:

```powershell
cd C:\VALCORE1
git pull
uv sync
```

---

## Next Steps

After completing this guide, you should:

1. ✅ Have VALCORE1 installed on Windows
2. ✅ Have VALCORE1 installed on ATOM
3. ✅ Have a backup on Google Drive
4. ✅ Be able to start and stop the system

**What to do next:**

1. **Enroll your voice:**
   - Run: `.\VALCORE1\05_Setup_Scripts\Voice_Enrollment\1_record_wake_word.ps1`
   - Run: `.\VALCORE1\05_Setup_Scripts\Voice_Enrollment\2_record_voice_profile.ps1`

2. **Read the documentation:**
   - `VALCORE1\04_Documentation\00_READ_ME_FIRST.md`
   - `VALCORE1\04_Documentation\QUICK_START_GUIDE.md`
   - `UV_GUIDE.md`

3. **Test voice commands:**
   - "Hey Val, what time is it?"
   - "Hey Val, switch to truck mode"
   - "Hey Val, open notepad"

4. **Set up remote access (optional):**
   - Install Tailscale on both machines
   - Run: `.\VALCORE1\06_Deployment\tailscale_setup.ps1`

---

## Support

If you run into issues:

1. Check the troubleshooting section above
2. Read: `VALCORE1\04_Documentation\TROUBLESHOOTING_GUIDE.md`
3. Run the full diagnostic suite:
   ```powershell
   .\VALCORE1\05_Setup_Scripts\Testing\RUN_ALL_TESTS.ps1
   ```
4. Check the logs:
   - `VALCORE1\logs\client_*.log`
   - `VALCORE1\logs\server_*.log`

---

**Congratulations! You're all set up! 🎉**

Enjoy your personal AI assistant, Val!

---

**Document Version:** 1.0
**Last Updated:** 2025-11-15
**For:** Ben (Master Builder)

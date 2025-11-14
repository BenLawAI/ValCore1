# VALCORE1 Quick Start Guide

**Version:** 1.0
**For:** Ben (System Owner)
**Setup Method:** Val-Assisted (Recommended)

---

## What is VALCORE1?

VALCORE1 is your personal AI voice assistant that combines:
- **Desktop PC** (RTX 5070 + RTX 4070) - Handles voice processing
- **ATOM Server** (Blackwell GB10, 128GB) - Runs large AI models

**Key Features:**
- Wake word detection ("Hey Val")
- Voice-authenticated commands
- Multi-room contexts (General, Truck, Invoice, Legal)
- Desktop automation
- Remote access via Tailscale

---

## Prerequisites

Before you start, ensure you have:

### Hardware:
- [x] Desktop PC with RTX 5070 (GPU 0) and RTX 4070 (GPU 1)
- [x] ATOM server with Blackwell GB10
- [x] Microphone (USB or built-in)
- [x] Network connection between desktop and ATOM

### Software:
- [x] Windows 10/11 on desktop
- [x] Linux on ATOM server (Ubuntu/Debian recommended)
- [x] Python 3.10 or later
- [x] Administrator access on both systems

---

## Setup Paths

You have **two options** for setup:

### Option 1: Val-Assisted Setup (RECOMMENDED)
**Time:** 2-3 hours
**Difficulty:** Easy
**Best for:** First-time setup

Val (Claude AI assistant) will guide you through every step with:
- Clear instructions
- Copy-paste commands
- Step-by-step verification
- Troubleshooting help

**To start:**
1. Open Claude (web or desktop)
2. Say: "I'm ready to set up VALCORE1. Let's follow the Phase 2 Master Protocol."
3. Val will take it from there!

### Option 2: Self-Guided Setup
**Time:** 3-5 hours
**Difficulty:** Medium
**Best for:** Experienced users

Follow this guide manually if you prefer to work independently.

---

## Quick Setup (Self-Guided)

### Step 1: Verify System (5 minutes)

Open PowerShell as Administrator:

```powershell
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\05_Setup_Scripts\Diagnostic

# Run diagnostics
.\1_test_gpu.ps1
.\2_test_cuda.ps1
.\3_test_microphone.ps1
.\5_test_python_env.ps1
```

**Expected:** All tests should pass (green)

### Step 2: Setup ATOM Server (30 minutes)

SSH into ATOM:

```bash
ssh ben@192.168.1.121
```

Install Ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Download AI model:

```bash
ollama pull qwen2.5:14b
```

Configure network access:

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo nano /etc/systemd/system/ollama.service.d/override.conf
```

Add:
```
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

Restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### Step 3: Setup Desktop Environment (20 minutes)

Install dependencies:

```powershell
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1
.\START_VALCORE1.bat
```

Configure firewall:

```powershell
cd .\05_Setup_Scripts\Windows
.\3_setup_firewall.ps1
```

Configure audio:

```powershell
.\4_setup_audio_devices.ps1
```

### Step 4: Create Voice Profile (30 minutes)

```powershell
cd ..\Voice_Enrollment

# Record wake word
.\1_record_wake_word.ps1

# Record voice profile
.\2_record_voice_profile.ps1

# Create embeddings
.\3_create_voice_embeddings.ps1

# Test verification
.\4_test_voice_verification.ps1
```

### Step 5: Configure Network (5 minutes)

Edit network config:

```powershell
notepad A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\01_Client_Brain\config\network_config.json
```

Update ATOM IP address.

Test connection:

```powershell
cd ..\Diagnostic
.\4_test_network_atom.ps1
```

### Step 6: Test System (10 minutes)

```powershell
cd ..\Testing
.\RUN_ALL_TESTS.ps1
```

**Expected:** All tests pass

### Step 7: First Launch (5 minutes)

Start ATOM server (in SSH):

```bash
cd /path/to/VALCORE1/02_Server_Brain
python main_server.py
```

Start desktop client:

```powershell
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1
.\START_VALCORE1.bat
```

**Test:**
Say: "Hey Val, what time is it?"

---

## Daily Usage

### Starting VALCORE1:

1. **Start ATOM server** (if not running):
   ```bash
   ssh ben@192.168.1.121
   cd /path/to/VALCORE1/02_Server_Brain
   python main_server.py
   ```

2. **Start desktop client:**
   ```powershell
   cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1
   .\START_VALCORE1.bat
   ```

3. **Look for system tray icon** (green = ready)

### Using Voice Commands:

1. Say wake word: "Hey Val"
2. Wait for confirmation
3. Say your command
4. Wait for response

### Switching Rooms:

- "Hey Val, switch to truck room"
- "Hey Val, switch to invoice room"
- "Hey Val, switch to legal room"
- "Hey Val, switch to general room"

### Emergency Stop:

Press: **Ctrl+Shift+Alt+V**

This immediately stops all VALCORE1 processes.

---

## Room Contexts

VALCORE1 has 4 specialized rooms:

### General Room
**Purpose:** Everyday conversations
**Best for:** General questions, casual chat
**System Prompt:** Helpful, conversational assistant

### Truck Room
**Purpose:** 2003 Dodge Ram with Hellcat engine swap
**Best for:** Mechanical questions, parts, troubleshooting
**System Prompt:** Expert mechanic specializing in Dodge/Hellcat

### Invoice Room
**Purpose:** Contractor invoicing and business
**Best for:** Creating invoices, tracking projects, business questions
**System Prompt:** Professional business assistant

### Legal Room
**Purpose:** Document review and legal assistance
**Best for:** Understanding contracts, legal documents, research
**System Prompt:** Legal research assistant (not a lawyer)

---

## Troubleshooting

### Voice not detected:
```powershell
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\05_Setup_Scripts\Diagnostic
.\3_test_microphone.ps1
```

### ATOM not responding:
```powershell
.\4_test_network_atom.ps1
```

### System tray icon missing:
```powershell
pip install pystray pillow
```

### For detailed troubleshooting:
See: `04_Documentation/TROUBLESHOOTING_GUIDE.md`

---

## Getting Help

### Phase 2 (Setup):
Ask Val: "I'm having trouble with VALCORE1 setup"

### Phase 3 (Validation):
Run Claude CLI validation:
```bash
claude code validate-valcore1
```

### Check logs:
```powershell
cd A:\000_START_HERE\VALCORE1_ROOT\Systems\VALCORE1\logs
dir
```

---

## Next Steps

After setup:

1. **Test all rooms** - Switch between contexts
2. **Try automation** - "Type hello in notepad"
3. **Set up Tailscale** - For remote access
4. **Configure startup** - Auto-launch with Windows
5. **Customize prompts** - Edit room contexts

---

## Key Files

**Configuration:**
- `01_Client_Brain/config/network_config.json` - ATOM connection
- `01_Client_Brain/config/voice_config.json` - Voice settings
- `01_Client_Brain/config/room_contexts.json` - Room behaviors

**Scripts:**
- `START_VALCORE1.bat` - Launch client
- `05_Setup_Scripts/` - All setup scripts

**Documentation:**
- `04_Documentation/` - All guides
- `07_Val_Protocols/PHASE2_MASTER_PROTOCOL.md` - Val's guide

---

## Tips for Success

1. **Start with Val-assisted setup** - It's much easier
2. **Test after each major step** - Don't skip validation
3. **Use the green PASS tests as confirmation** - Red means stop and fix
4. **Keep ATOM server running** - Desktop needs it for LLM
5. **Practice wake word** - Say it consistently
6. **Emergency stop is your friend** - Don't hesitate to use it

---

## System Status Indicators

**System Tray Icon Colors:**
- 🟢 **Green:** Listening, ready for wake word
- 🟡 **Yellow:** Processing your command
- 🔴 **Red:** Error or disconnected
- ⚪ **Gray:** Microphone disabled

---

**Ready to start?**

Choose your path:
- **Easy:** Ask Val to guide you (recommended)
- **DIY:** Follow this guide step by step

Either way, you'll have a working AI voice assistant soon!

---

*VALCORE1 - Your Personal AI Assistant*
*Version 1.0 - November 2025*

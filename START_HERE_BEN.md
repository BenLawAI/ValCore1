# 👋 HEY BEN - START HERE!

**Welcome to VALCORE1 - Your Personal AI Assistant "Val"**

This file will guide you to the right documentation based on what you want to do.

---

## 🚀 I'm Ready to Install! Where do I start?

**→ Read:** `QUICK_SETUP_CHECKLIST.md`

This is a 41-step checklist you can print out and follow. Each step takes 2-5 minutes.

**Total time:** ~1.5 hours

**What you'll do:**
1. Download VALCORE1
2. Install on Windows
3. Install on ATOM server
4. Backup to Google Drive
5. Run your first test

---

## 📖 I want detailed instructions with explanations

**→ Read:** `COMPLETE_SETUP_GUIDE.md`

This is the complete guide (40+ pages) with:
- Step-by-step instructions
- Screenshots placeholders
- Troubleshooting for every step
- Background information
- Multiple options for each step

**Best for:** If you want to understand what you're doing, not just copy-paste commands.

---

## ☁️ How do I backup to Google Drive?

**→ Read:** `GOOGLE_DRIVE_SETUP.md`

This guide covers:
- 3 different methods (easy, manual, advanced)
- What to backup and what to skip
- How much space you need
- Automatic backup setup
- How to restore from backup

---

## ⚡ I just want the quick commands (I know what I'm doing)

### Download:
```powershell
# Go to: https://github.com/BenLawAI/ValCore1
# Download ZIP and extract to C:\VALCORE1
```

### Install on Windows:
```powershell
# Install UV:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Setup:
cd C:\VALCORE1
.\setup_with_uv.ps1

# Add Picovoice key:
# Edit: VALCORE1\01_Client_Brain\config\voice_config.json
```

### Install on ATOM:
```bash
# Transfer files:
scp -r C:\VALCORE1 ben@192.168.1.121:~/

# Install:
ssh ben@192.168.1.121
cd ~/ValCore1
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
./setup_with_uv.sh

# Install Ollama:
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull qwen2.5:14b
```

### Run:
```bash
# ATOM:
uv run python VALCORE1/02_Server_Brain/main_server.py

# Windows:
uv run python VALCORE1\01_Client_Brain\main_client.py
```

---

## 🔧 What is UV and how do I use it?

**→ Read:** `UV_GUIDE.md`

UV is the modern Python package manager we're using (10-100x faster than pip).

This guide covers:
- What UV is and why we use it
- Common UV commands
- How to add/remove packages
- How to run Python scripts with UV
- Troubleshooting UV issues

---

## 📂 What files are where? (File structure)

```
C:\VALCORE1\
├── START_HERE_BEN.md               ← YOU ARE HERE
├── QUICK_SETUP_CHECKLIST.md        ← Print this! 41 steps
├── COMPLETE_SETUP_GUIDE.md         ← Full detailed guide
├── GOOGLE_DRIVE_SETUP.md           ← Backup guide
├── UV_GUIDE.md                     ← UV package manager guide
├── README.md                       ← Project overview
│
├── VALCORE1\                       ← Main system code
│   ├── 01_Client_Brain\            ← Windows desktop code
│   ├── 02_Server_Brain\            ← ATOM server code
│   ├── 03_Shared\                  ← Shared utilities
│   ├── 04_Documentation\           ← User guides
│   ├── 05_Setup_Scripts\           ← PowerShell scripts
│   ├── 06_Deployment\              ← Deployment scripts
│   └── 07_Val_Protocols\           ← Val's protocols
│
├── pyproject.toml                  ← UV configuration
├── uv.lock                         ← Dependency versions
├── setup_with_uv.ps1               ← Windows auto-setup
├── setup_with_uv.sh                ← Linux auto-setup
│
└── .venv\                          ← Virtual environment (created by UV)
```

---

## 🎯 Quick Decision Tree

**Are you installing for the first time?**
- YES → Use `QUICK_SETUP_CHECKLIST.md` (easiest)
- NO → Skip to "I already installed, now what?"

**Do you want to understand every step?**
- YES → Use `COMPLETE_SETUP_GUIDE.md`
- NO → Use `QUICK_SETUP_CHECKLIST.md`

**Do you want automatic Google Drive backup?**
- YES → Read `GOOGLE_DRIVE_SETUP.md` after installing
- NO → You can skip this

---

## 🆘 I'm stuck! Help!

### Installation Issues:

**→ Check:** `COMPLETE_SETUP_GUIDE.md` → "Troubleshooting" section

Common issues:
- "uv: command not found" → Reopen PowerShell as Admin
- "CUDA not available" → Install NVIDIA drivers
- "Cannot connect to ATOM" → Check IP address in config
- "Microphone not detected" → Check Windows sound settings

### Running Issues:

**→ Check:** `VALCORE1\04_Documentation\TROUBLESHOOTING_GUIDE.md`

Or run diagnostics:
```powershell
.\VALCORE1\05_Setup_Scripts\Testing\RUN_ALL_TESTS.ps1
```

### UV Issues:

**→ Check:** `UV_GUIDE.md` → "Troubleshooting" section

---

## 📚 I want to read ALL the documentation

Here's everything in order:

### Getting Started:
1. `START_HERE_BEN.md` ← You are here
2. `QUICK_SETUP_CHECKLIST.md` ← Do this first
3. `COMPLETE_SETUP_GUIDE.md` ← Read for details

### Installation:
4. `UV_GUIDE.md` ← Learn about UV
5. `GOOGLE_DRIVE_SETUP.md` ← Backup your work

### Using VALCORE1:
6. `VALCORE1\04_Documentation\00_READ_ME_FIRST.md` ← Start here after install
7. `VALCORE1\04_Documentation\QUICK_START_GUIDE.md` ← Quick reference
8. `VALCORE1\04_Documentation\ARCHITECTURE_OVERVIEW.md` ← How it works
9. `VALCORE1\04_Documentation\TROUBLESHOOTING_GUIDE.md` ← Fix problems

### Advanced:
10. `VALCORE1\07_Val_Protocols\PHASE2_MASTER_PROTOCOL.md` ← Val's protocol
11. `VALCORE1\SYSTEM_AUDIT_REPORT.md` ← Verification report
12. `README.md` ← Project overview

---

## 🎉 I Already Installed - Now What?

**Congratulations!** Here's what to do next:

### 1. Enroll Your Voice (10 minutes):
```powershell
cd C:\VALCORE1
.\VALCORE1\05_Setup_Scripts\Voice_Enrollment\1_record_wake_word.ps1
.\VALCORE1\05_Setup_Scripts\Voice_Enrollment\2_record_voice_profile.ps1
.\VALCORE1\05_Setup_Scripts\Voice_Enrollment\3_create_voice_embeddings.ps1
```

### 2. Run Tests (5 minutes):
```powershell
.\VALCORE1\05_Setup_Scripts\Testing\RUN_ALL_TESTS.ps1
```

### 3. Start Using Val:

**Start the system:**
```powershell
# On ATOM (in SSH):
uv run python VALCORE1/02_Server_Brain/main_server.py

# On Windows:
uv run python VALCORE1\01_Client_Brain\main_client.py
```

**Try these commands:**
- "Hey Val, what time is it?"
- "Hey Val, switch to truck mode"
- "Hey Val, open notepad"
- "Hey Val, take a screenshot"

### 4. Read the User Guide:
```powershell
Get-Content VALCORE1\04_Documentation\QUICK_START_GUIDE.md
```

---

## 💡 Pro Tips

1. **Print the checklist** (`QUICK_SETUP_CHECKLIST.md`) and check off steps as you go

2. **Keep this folder** (`C:\VALCORE1`) - don't move it after installing

3. **Backup to Google Drive** before making changes (see `GOOGLE_DRIVE_SETUP.md`)

4. **Run diagnostics** if something isn't working:
   ```powershell
   .\VALCORE1\05_Setup_Scripts\Testing\RUN_ALL_TESTS.ps1
   ```

5. **Check the logs** if Val isn't responding:
   ```powershell
   Get-Content VALCORE1\logs\client_*.log -Tail 50
   ```

---

## ❓ Frequently Asked Questions

**Q: How long does installation take?**
A: About 1.5 hours total (mostly waiting for downloads)

**Q: Do I need to know Python?**
A: No! Just copy-paste the commands from the checklist.

**Q: Will this work without ATOM server?**
A: Partially. Voice commands work, but you'll have limited LLM capabilities.

**Q: Can I use this on my laptop when away from home?**
A: Yes! Set up Tailscale for remote access (see deployment scripts).

**Q: How much does this cost?**
A: Free! Except Picovoice wake word (free tier available).

**Q: Is my data private?**
A: Yes! Everything runs locally. No cloud services (except optional Google Drive backup).

**Q: Can I customize Val's personality?**
A: Yes! Edit the room contexts in `VALCORE1\01_Client_Brain\config\room_contexts.json`

---

## 🔗 Quick Links

- **GitHub Repository:** https://github.com/BenLawAI/ValCore1
- **Picovoice Console:** https://console.picovoice.ai/
- **Google Drive:** https://drive.google.com
- **UV Documentation:** https://docs.astral.sh/uv/
- **Ollama Website:** https://ollama.com

---

## 📞 What to Do If You're Stuck

1. **Read the troubleshooting section** in the guide you're following
2. **Run diagnostics:**
   ```powershell
   .\VALCORE1\05_Setup_Scripts\Testing\RUN_ALL_TESTS.ps1
   ```
3. **Check the logs:**
   ```powershell
   Get-Content VALCORE1\logs\client_*.log -Tail 50
   ```
4. **Read the detailed troubleshooting guide:**
   ```powershell
   Get-Content VALCORE1\04_Documentation\TROUBLESHOOTING_GUIDE.md
   ```

---

## 🎯 Your Next Step

**If you haven't installed yet:**
→ Open `QUICK_SETUP_CHECKLIST.md` and start at step 1

**If you have installed:**
→ Open `VALCORE1\04_Documentation\00_READ_ME_FIRST.md`

---

**You've got this, Ben! Val is waiting to help you. 🚀**

---

**Last Updated:** 2025-11-15
**Version:** 1.0.0

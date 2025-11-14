# Welcome to VALCORE1 Setup

## Hey Boss!

This is your complete setup guide for VALCORE1 - your AI voice assistant system.

---

## What is VALCORE1?

VALCORE1 is a voice-controlled AI assistant that:
- Listens for "Hey Val" wake word
- Runs on your desktop (RTX 5070 + RTX 4070)
- Connects to your ATOM server for powerful LLM responses
- Has 4 specialized rooms: General, Truck, Invoice, Legal
- Types responses into active windows
- Remembers all conversations with semantic search
- Works offline with automatic fallback LLM

---

## 3-Phase Setup Process

### Phase 1: Claude Code Web (COMPLETE ✅)
**Status:** DONE - All code has been generated

Claude Code Web has created:
- Complete Python codebase (Client Brain + Server Brain)
- All configuration files
- PowerShell diagnostic scripts
- Setup protocols
- Documentation

### Phase 2: Val + Ben Setup (YOU ARE HERE 👉)
**Your Role:** Follow Val's step-by-step instructions

1. Start a NEW chat with Claude (use Sonnet 4.5 model)
2. Say: "I'm ready to set up VALCORE1. I have the Setup Assistant files."
3. Upload this document to Val: `01_FOR_VAL_SONNET/PHASE2_MASTER_PROTOCOL.md`
4. Follow Val's instructions exactly
5. Val will guide you through:
   - Hardware diagnostics (GPU, CUDA, mic, network)
   - Windows integration (startup, firewall, permissions)
   - Voice enrollment (record wake word and voice profile)
   - First run tests

### Phase 3: Claude CLI Validation (FINAL STEP)
**Automatic:** Claude CLI receives Val's diagnostics and fixes any issues

---

## Prerequisites Check

Before starting, verify you have:

### Desktop (Client Brain)
- [  ] Windows 10 or 11
- [  ] NVIDIA RTX 5070 (12GB) installed
- [  ] NVIDIA RTX 4070 (12GB) installed
- [  ] NVIDIA drivers 550+ installed
- [  ] CUDA 12.1+ installed
- [  ] Python 3.10 or higher installed
- [  ] Microphone connected and working
- [  ] Administrator access to Windows

### ATOM Server (Server Brain)
- [  ] Linux (Ubuntu/Debian preferred)
- [  ] NVIDIA Blackwell GB10 (128GB unified memory)
- [  ] Network accessible at 192.168.1.121
- [  ] Port 11434 open for Ollama
- [  ] Ollama installed (or ready to install)

### Network
- [  ] Desktop can ping 192.168.1.121
- [  ] No firewall blocking port 11434

---

## Quick Start Path

**Option A: Full Setup with Val (RECOMMENDED)**
1. Go to `01_FOR_VAL_SONNET/`
2. Upload `PHASE2_MASTER_PROTOCOL.md` to Val (Sonnet 4.5)
3. Follow Val's guidance step-by-step
4. Val will handle all troubleshooting

**Option B: Quick Test (Advanced Users)**
1. Extract VALCORE1 to `A:\000_START_HERE\VALCORE1_ROOT\Systems\`
2. Get Picovoice access key from https://console.picovoice.ai/
3. Update `VALCORE1/01_Client_Brain/config/voice_config.json`
4. Run `VALCORE1/START_VALCORE1.bat`
5. Say "Hey Val, what time is it?"

**Option C: Manual Setup**
1. Read `05_Documentation/SETUP_GUIDE.md`
2. Follow step-by-step instructions
3. Run diagnostic scripts yourself
4. Troubleshoot using `05_Documentation/TROUBLESHOOTING.md`

---

## Important Files

### For You (Ben)
- **THIS FILE** - Start here
- `03_SCRIPTS_FOR_BEN/` - PowerShell scripts you'll run
- `04_VAL_ERROR_LOG/` - Val will save diagnostic results here

### For Val (Sonnet 4.5)
- `01_FOR_VAL_SONNET/PHASE2_MASTER_PROTOCOL.md` - Val's complete guide
- `01_FOR_VAL_SONNET/ERROR_RESPONSES.md` - Troubleshooting templates
- `01_FOR_VAL_SONNET/HANDOFF_TO_CLI.md` - Final handoff format

### For Claude CLI
- `02_FOR_CLAUDE_CLI/PHASE3_VALIDATION.md` - Validation checklist
- `02_FOR_CLAUDE_CLI/CODE_FIXES.md` - How to apply fixes

---

## System Overview

```
YOUR DESKTOP                           ATOM SERVER
┌─────────────────────┐               ┌──────────────────┐
│  Client Brain       │               │  Server Brain    │
│  ┌───────────────┐  │   Network    │  ┌────────────┐  │
│  │ RTX 5070      │  │◄─────────────┤  │ Blackwell  │  │
│  │ Voice System  │  │   11434      │  │ GB10       │  │
│  └───────────────┘  │               │  │            │  │
│  ┌───────────────┐  │               │  │ Ollama     │  │
│  │ RTX 4070      │  │               │  │ qwen2.5    │  │
│  │ Fallback LLM  │  │               │  │ 14b-70b    │  │
│  └───────────────┘  │               │  └────────────┘  │
└─────────────────────┘               └──────────────────┘
         │                                      │
         │                                      │
    Your Voice ──►  "Hey Val"  ──►       LLM Response
```

---

## Room Contexts

VALCORE1 has 4 specialized rooms. Switch with: "Hey Val, switch to [room name]"

### 🏠 General (Default)
- General purpose assistant
- Code help, research, daily tasks
- Conversational and helpful

### 🚗 Truck
- Focus: Your 2003 Dodge Ram 1500 2WD
- Hellcat swap project (750hp target)
- Automotive diagnostics and maintenance
- Technical but clear

### 📄 Invoice
- Contractor invoice generation
- 66-character width receipt formatting
- 35% markup calculations
- Military discount applications
- Precise and professional

### ⚖️ Legal
- Legal document assistance
- Contract review
- Compliance guidance
- **Always includes "not a lawyer" disclaimer**
- Careful and thorough

---

## Common Questions

**Q: How long does setup take?**
A: With Val's help: 2-3 hours total
   - Hardware diagnostics: 30 min
   - Windows integration: 15 min
   - Voice enrollment: 45 min
   - First run tests: 30 min
   - Buffer time: 30 min

**Q: What if something goes wrong?**
A: Val will troubleshoot with you in real-time. Every script has clear error messages and fixes.

**Q: Do I need to know Python?**
A: No! All scripts are copy/paste PowerShell commands. Val tells you exactly what to run.

**Q: Can I use this without ATOM server?**
A: Yes! The system has fallback to local 7-13B model on RTX 4070. Slower but works offline.

**Q: Is my voice data private?**
A: Yes! Everything runs locally. Voice profiles never leave your computer.

---

## Next Steps

1. ✅ You've read this file
2. ➡️ Start a chat with Claude (Sonnet 4.5)
3. ➡️ Upload `01_FOR_VAL_SONNET/PHASE2_MASTER_PROTOCOL.md` to Val
4. ➡️ Say: "I'm ready to set up VALCORE1"
5. ➡️ Follow Val's instructions

---

## Need Help?

- **During setup:** Ask Val (Sonnet 4.5) - Val has complete troubleshooting protocols
- **After setup:** See `05_Documentation/TROUBLESHOOTING.md`
- **For advanced customization:** See `05_Documentation/` folder

---

## System Status

**Current Version:** v0.50 (50% Complete - All Core Code Implemented)

**What's Working:**
- ✅ Complete Python codebase (Client + Server)
- ✅ All configuration files
- ✅ Core voice system
- ✅ Server connection with fallback
- ✅ Room management
- ✅ Memory compression
- ✅ Automation system

**What Needs Setup:**
- ⏳ Voice profile enrollment (you'll do this with Val)
- ⏳ Picovoice access key (free, takes 2 minutes)
- ⏳ Windows permissions and firewall
- ⏳ First run validation

---

**Ready to start? Open `01_FOR_VAL_SONNET/PHASE2_MASTER_PROTOCOL.md` and let's go!**

---

*Created for Ben (Master Builder) by Claude Code Web*
*Date: 2025-11-14*

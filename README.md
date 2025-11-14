# VALCORE1 - AI Voice Assistant System

## Overview

VALCORE1 is a comprehensive AI voice assistant system designed for Ben's desktop and server infrastructure.

**Status:** 🟡 **Initial Structure Generated - Completion Required**

This repository contains the **foundational structure** and **core modules** for VALCORE1. Many components have been created, but the system requires additional implementation by Claude CLI or Val (Sonnet 4.5) to be production-ready.

## System Architecture

### Client Brain (Ben's Desktop)
- **Hardware:** RTX 5070 (GPU 0) + RTX 4070 (GPU 1)
- **GPU 0 Tasks:** Faster-Whisper STT, Kokoro TTS, Wake Word
- **GPU 1 Tasks:** Fallback LLM (7-13B model)
- **Location:** `01_Client_Brain/`

### Server Brain (ATOM)
- **Hardware:** NVIDIA Blackwell GB10, 128GB unified memory
- **Tasks:** Large LLM (14b-70b), Vector search, Memory compression
- **Location:** `02_Server_Brain/`

### Communication
- **Local Network:** 192.168.1.121:11434
- **Remote Access:** Tailscale (scripts in `06_Deployment/`)
- **Protocol:** HTTP/JSON with retry logic and fallback

## What Has Been Created

### ✅ Complete
1. **Directory Structure** - Full hierarchy for all components
2. **Configuration Files** - All JSON configs with complete schemas
3. **Core Client Modules:**
   - `voice_system_unified.py` - Faster-Whisper + Kokoro + Porcupine + Resemblyzer
   - `server_bridge.py` - ATOM connection with retry and fallback
   - `small_llm_interface.py` - Local LLM fallback on RTX 4070
   - `automation.py` - PyAutoGUI automation with undo
4. **Requirements Files** - Client and server dependencies
5. **Main Entry Point** - `main_client.py` with complete logic
6. **Startup Script** - `START_VALCORE1.bat` for Windows

### 🟡 Partial / Needs Completion
1. **Client Brain Modules** (need implementation):
   - `system_tray.py` - Windows system tray integration
   - `health_monitor.py` - GPU/RAM/network monitoring
   - `emergency_stop.py` - Panic hotkey (Ctrl+Shift+Alt+V)
   - `network_fallback.py` - Offline queue and sync protocol

2. **Server Brain Modules** (need implementation):
   - `large_llm_interface.py` - Ollama interface with streaming
   - `librarian.py` - FAISS vector search + semantic memory
   - `memory_compression.py` - Daily/monthly/yearly compression
   - `room_manager.py` - Context switching system
   - `client_bridge.py` - Flask server for client requests

3. **Shared Modules** (need implementation):
   - `network_protocol.py` - JSON message schema
   - `common_utils.py` - Shared utilities
   - `performance_profiler.py` - Latency tracking

4. **PowerShell Scripts** (need creation):
   - Diagnostic scripts (GPU, CUDA, mic, network, Python)
   - Windows setup scripts (startup, firewall, permissions)
   - Voice enrollment scripts (wake word, profile training)
   - Testing scripts (10 validation tests)

5. **Protocol Documents** (need creation):
   - Val's Phase 2 Master Protocol (guides Ben through setup)
   - Claude CLI Phase 3 Validation (final validation checklist)
   - Error response templates
   - Handoff documentation

6. **MCP Tools Registry** (need creation):
   - 5 pre-configured MCP servers (filesystem, Drive, Gmail, Calendar, web search)
   - Tool discovery and registration system

7. **Documentation** (need creation):
   - SETUP_GUIDE.md
   - VOICE_COMMANDS.md
   - TROUBLESHOOTING.md
   - GPU_OPTIMIZATION.md
   - REMOTE_ACCESS.md

## 🚀 Getting Started

### Step 1: Install Dependencies

**Windows (Client):**
```powershell
# Quick check what's already installed
.\check_dependencies.ps1

# Download and install everything
.\download_dependencies.ps1
```

**Linux (Server):**
```bash
# Download and install server dependencies
chmod +x download_dependencies_server.sh
./download_dependencies_server.sh
```

📖 **See:** `DEPENDENCY_SCRIPTS_README.md` for detailed documentation

### Step 2: Follow Setup Instructions

📖 **See:** `SETUP_INSTRUCTIONS.md` for step-by-step guided setup

Copy each section and paste it to Claude for interactive guidance through:
- Prerequisites verification
- Python environment setup
- Picovoice wake word configuration
- ATOM server setup
- First run and testing

### Step 3: Configure & Run

1. Get Picovoice access key from [console.picovoice.ai](https://console.picovoice.ai/)
2. Update `VALCORE1/01_Client_Brain/config/voice_config.json`
3. Run: `python VALCORE1/01_Client_Brain/main_client.py`
4. Say "Hey Val" to activate!

---

## Quick Start (Legacy - When Complete)

### For Ben (After Full Implementation)
1. Extract VALCORE1 to `A:\000_START_HERE\VALCORE1_ROOT\Systems\`
2. Run `START_VALCORE1.bat`
3. Say "Hey Val" to activate

### For Val (Phase 2 Setup Assistance)
1. Review `00_SETUP_ASSISTANT/01_FOR_VAL_SONNET/PHASE2_MASTER_PROTOCOL.md`
2. Guide Ben through diagnostics and setup
3. Document issues in `04_VAL_ERROR_LOG/`

### For Claude CLI (Phase 3 Validation)
1. Review `00_SETUP_ASSISTANT/02_FOR_CLAUDE_CLI/PHASE3_VALIDATION.md`
2. Apply code fixes from Val's diagnostics
3. Run test suite and validate deployment

## Configuration

### Key Configuration Files
- `01_Client_Brain/config/gpu_config.json` - GPU device assignments
- `01_Client_Brain/config/network_config.json` - ATOM connection settings
- `01_Client_Brain/config/voice_config.json` - Voice system parameters
- `01_Client_Brain/config/room_contexts.json` - Room-based contexts (general, truck, invoice, legal)
- `02_Server_Brain/config/compression_strategy.json` - Memory compression rules

### Important: Porcupine Access Key
Before wake word detection works, you need to:
1. Get a free access key from [Picovoice Console](https://console.picovoice.ai/)
2. Update `01_Client_Brain/config/voice_config.json`:
   ```json
   "wake_word": {
     "access_key": "YOUR_ACTUAL_KEY_HERE"
   }
   ```

## Voice Commands (When Complete)

### System Control
- "Hey Val mic on/off" - Toggle microphone
- "Hey Val stop" / "Hey Val undo" - Emergency stop

### Room Switching
- "Hey Val switch to truck" - Automotive context
- "Hey Val switch to invoice" - Invoice generation
- "Hey Val switch to legal" - Legal documents
- "Hey Val switch to general" - General assistant

### Computer Control
- "Hey Val open [app]" - Launch application
- "Hey Val take screenshot" - Capture screen
- "Hey Val type this [text]" - Auto-type response

## Room Contexts

### General
- General purpose assistant
- Code help, research, daily tasks
- Temperature: 0.7

### Truck
- 2003 Dodge Ram 1500 2WD maintenance
- Hellcat swap project (750hp target)
- Automotive diagnostics
- Temperature: 0.5

### Invoice
- Contractor invoice generation
- 66-char width receipt formatting
- 35% markup calculations
- Military discounts
- Temperature: 0.3

### Legal
- Legal document assistance
- Contract review
- Compliance guidance
- **Always includes disclaimer about not being a lawyer**
- Temperature: 0.3

## Development Status

### Completion Estimate
- **Core Structure:** 100% ✅
- **Configuration:** 100% ✅
- **Client Brain Code:** 40% 🟡
- **Server Brain Code:** 0% ❌
- **Shared Modules:** 0% ❌
- **PowerShell Scripts:** 0% ❌
- **Setup Protocols:** 0% ❌
- **MCP Tools:** 0% ❌
- **Documentation:** 15% 🟡

**Overall: ~25% Complete**

## Next Steps

### Option 1: Continue with Claude CLI
1. Review this structure
2. Implement remaining Python modules (see IMPLEMENTATION_GUIDE.md)
3. Create all PowerShell scripts
4. Write protocol documents for Val
5. Test and validate

### Option 2: Hand Off to Val (Sonnet 4.5)
1. Val reviews the structure
2. Val creates protocol documents first
3. Val guides Ben through hardware diagnostics
4. Val documents issues for Claude CLI to fix
5. Claude CLI applies fixes and completes implementation

### Option 3: Iterative Approach
1. Implement one subsystem at a time (e.g., voice system only)
2. Test each component
3. Add next component
4. Repeat until complete

## Repository Structure

```
ValCore1/
├── VALCORE1/                      # Main system
│   ├── 01_Client_Brain/          # Desktop client (RTX 5070 + 4070)
│   ├── 02_Server_Brain/          # ATOM server (Blackwell GB10)
│   ├── 03_Shared/                # Shared modules
│   ├── 04_Tools_Registry/        # MCP servers
│   ├── 05_Documentation/         # User documentation
│   └── 06_Deployment/            # Deployment scripts
├── 00_SETUP_ASSISTANT/           # Setup protocols for Val + Ben
│   ├── 01_FOR_VAL_SONNET/       # Val's guidance protocols
│   ├── 02_FOR_CLAUDE_CLI/       # CLI validation procedures
│   ├── 03_SCRIPTS_FOR_BEN/      # PowerShell scripts Ben runs
│   └── 04_VAL_ERROR_LOG/        # Diagnostic results
├── Library/                       # Persistent memory storage
│   ├── daily/                    # Daily conversations
│   ├── monthly/                  # Monthly summaries
│   ├── yearly/                   # Yearly archives
│   ├── backups/                  # Pre-compression backups
│   └── rooms/                    # Room-specific contexts
└── START_VALCORE1.bat            # Windows startup script
```

## Technical Requirements

### Ben's Desktop (Client)
- Windows 10/11
- NVIDIA RTX 5070 (12GB) - GPU 0
- NVIDIA RTX 4070 (12GB) - GPU 1
- NVIDIA drivers 550+ with CUDA 12.1+
- Python 3.10+
- Microphone input device

### ATOM Server
- Linux (Ubuntu/Debian)
- NVIDIA Blackwell GB10 (128GB unified memory)
- Ollama installed
- Network accessible from desktop (192.168.1.121:11434)

## License

This is Ben's personal AI assistant system. Not for public distribution.

## Support

For issues, questions, or implementation help:
1. Review `IMPLEMENTATION_GUIDE.md` for details on missing components
2. Check `05_Documentation/TROUBLESHOOTING.md` (when created)
3. Consult Val (Sonnet 4.5) for setup assistance
4. Use Claude CLI for code implementation and validation

---

**Created by:** Claude Code Web
**For:** Ben (Master Builder)
**Date:** 2025-11-14
**Version:** 0.25 (25% Complete)

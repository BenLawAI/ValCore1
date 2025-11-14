# VALCORE1 Architecture Overview

**Version:** 1.0
**System Type:** Distributed AI Voice Assistant
**Architecture:** Client-Server with Multi-GPU

---

## System Overview

VALCORE1 is a sophisticated voice-controlled AI assistant that distributes workload across two computing systems:

### Desktop System (Client Brain)
- **Primary Role:** Voice processing, user interaction, desktop automation
- **Hardware:** RTX 5070 (voice) + RTX 4070 (fallback LLM)
- **OS:** Windows 10/11
- **Components:** Voice input/output, speaker verification, system control

### ATOM Server (Server Brain)
- **Primary Role:** Large language model inference
- **Hardware:** NVIDIA Blackwell GB10, 128GB RAM
- **OS:** Linux (Ubuntu/Debian)
- **Components:** Ollama, vector database, memory compression

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DESKTOP SYSTEM                           │
│                       (Client Brain)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Voice      │      │   Server     │      │  Automation  │ │
│  │   System     │─────▶│   Bridge     │─────▶│   Engine     │ │
│  │  (RTX 5070)  │      │              │      │              │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│       │                       │                       │        │
│       │ Audio                 │ HTTP/JSON             │ UI     │
│       ▼                       ▼                       ▼        │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │  Microphone  │      │   Network    │      │   Desktop    │ │
│  │   Speaker    │      │   Fallback   │      │   Control    │ │
│  └──────────────┘      │ (RTX 4070)   │      └──────────────┘ │
│                        └──────────────┘                        │
│                               │                                │
└───────────────────────────────┼────────────────────────────────┘
                                │
                                │ LAN / Tailscale
                                │ HTTP/JSON Protocol
                                │
┌───────────────────────────────┼────────────────────────────────┐
│                               │                                │
│                        ATOM SERVER                             │
│                       (Server Brain)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Client     │      │   LLM        │      │  Librarian   │ │
│  │   Bridge     │─────▶│  Interface   │─────▶│  (FAISS)     │ │
│  │  (Flask)     │      │  (Ollama)    │      │              │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│       │                       │                       │        │
│       │                       │ GPU (Blackwell)       │        │
│       ▼                       ▼                       ▼        │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Room       │      │   Memory     │      │  Compression │ │
│  │  Manager     │      │   Store      │      │   System     │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Client Brain (Desktop)

#### 1. Voice System Unified (`voice_system_unified.py`)

**Responsibilities:**
- Audio capture from microphone
- Wake word detection (Porcupine)
- Speech-to-text (Faster-Whisper on RTX 5070)
- Speaker verification (Resemblyzer)
- Text-to-speech (Kokoro)

**GPU Usage:**
- Device: RTX 5070 (CUDA device 0)
- VRAM: ~4-6GB during active use
- Models: Faster-Whisper large-v3-turbo

**Key Features:**
- Dynamic microphone detection
- Background listening thread
- Voice activity detection
- Speaker embeddings comparison

#### 2. Server Bridge (`server_bridge.py`)

**Responsibilities:**
- Communication with ATOM server
- Request/response handling
- Automatic retry logic
- Fallback to local LLM on failure

**Protocol:**
- HTTP/JSON over LAN or Tailscale
- Timeout: 30 seconds default
- Max retries: 3 with exponential backoff

**Fallback Behavior:**
```python
if atom_unreachable:
    use_small_llm_on_rtx_4070()
```

#### 3. Small LLM Interface (`small_llm_interface.py`)

**Responsibilities:**
- Offline LLM inference
- Emergency backup when ATOM down
- Limited but functional responses

**GPU Usage:**
- Device: RTX 4070 (CUDA device 1)
- Model: qwen2.5:7b
- VRAM: ~4GB

#### 4. Automation Engine (`automation.py`)

**Responsibilities:**
- Desktop control (PyAutoGUI)
- Window management
- Keyboard/mouse simulation
- Screenshot capture & OCR

**Safety Features:**
- Refuses console window interaction
- Emergency undo buffer (last 3 actions)
- Panic stop: Ctrl+Shift+Alt+V

#### 5. System Tray (`system_tray.py`)

**Responsibilities:**
- Visual status indicator
- Quick controls
- Microphone toggle
- Exit handler

**Icon States:**
- 🟢 Green: Listening
- 🟡 Yellow: Processing
- 🔴 Red: Error
- ⚪ Gray: Disabled

#### 6. Health Monitor (`health_monitor.py`)

**Responsibilities:**
- GPU temperature/utilization
- RAM usage tracking
- Network latency monitoring
- CSV logging for analysis

**Thresholds:**
- GPU: 85°C warning, 90°C critical
- RAM: 85% warning
- Disk: <10GB warning
- Network: >200ms latency warning

#### 7. Emergency Stop (`emergency_stop.py`)

**Responsibilities:**
- Panic button handler
- State checkpoint saving
- Process termination
- Recovery script generation

**Hotkey:** Ctrl+Shift+Alt+V

#### 8. Network Fallback (`network_fallback.py`)

**Responsibilities:**
- Offline operation queue
- Automatic sync when reconnected
- Conflict resolution
- State persistence

---

### Server Brain (ATOM)

#### 1. Large LLM Interface (`large_llm_interface.py`)

**Responsibilities:**
- Ollama client management
- LLM request handling
- Streaming support
- Model selection per room

**Models:**
- Primary: qwen2.5:14b (8GB VRAM)
- Optional: qwen2.5:70b (40GB VRAM)
- Format: Ollama's GGUF quantized

**GPU Usage:**
- Device: Blackwell GB10
- Context: 32K tokens
- Batch size: Optimized per model

#### 2. Librarian (`librarian.py`)

**Responsibilities:**
- Vector database (FAISS)
- Semantic memory search
- Conversation storage
- Room-based organization

**Embeddings:**
- Model: sentence-transformers/all-MiniLM-L6-v2
- Dimensions: 384
- Similarity: Cosine (IndexFlatIP)
- Threshold: 0.7 for relevance

**Storage Format:**
```python
{
    "text": "conversation text",
    "embedding": [384-dim vector],
    "room": "general",
    "timestamp": "ISO-8601",
    "metadata": {...}
}
```

#### 3. Memory Compression (`memory_compression.py`)

**Responsibilities:**
- Automatic compression (2am daily)
- Semantic importance scoring
- Token budget management
- Historical rollup (daily→monthly→yearly)

**Importance Tiers:**
- High: >0.9 (always preserve)
- Medium: 0.7-0.9 (context-dependent)
- Low: 0.5-0.7 (summary only)
- Discard: <0.5

**Token Budgets:**
- Daily: 1500 tokens
- Monthly: 4000 tokens
- Yearly: 8000 tokens

#### 4. Room Manager (`room_manager.py`)

**Responsibilities:**
- Room context switching
- Configuration management
- Session tracking
- Statistics collection

**Rooms:**
- General: Conversational assistant
- Truck: Automotive expert (Dodge/Hellcat)
- Invoice: Business/contractor assistant
- Legal: Document analysis assistant

#### 5. Client Bridge (`client_bridge.py`)

**Responsibilities:**
- Flask HTTP server (port 5000)
- Request routing
- CORS handling
- Error responses

**API Endpoints:**
```
GET  /api/health          - Health check
POST /api/process         - Process voice input
POST /api/search          - Search memories
POST /api/room/switch     - Change room
GET  /api/rooms           - List rooms
```

---

### Shared Components

#### 1. Network Protocol (`network_protocol.py`)

**Message Types:**
- VoiceInputMessage
- LLMResponseMessage
- CommandMessage
- ErrorMessage
- HealthCheckMessage

**Schema Validation:**
- Pydantic models
- UUID event IDs
- ISO-8601 timestamps
- Type-safe payloads

#### 2. Common Utils (`common_utils.py`)

**Utilities:**
- JSON config loading/saving
- Timestamp generation
- Token counting
- File sanitization
- Duration formatting

#### 3. Performance Profiler (`performance_profiler.py`)

**Metrics:**
- Task latency (ms)
- GPU utilization (%)
- RAM usage (MB)
- CSV logging

**Usage:**
```python
with profiler.measure("transcribe_audio"):
    text = whisper.transcribe(audio)
```

---

## Data Flow

### Voice Command Processing:

```
1. User speaks → Microphone
2. Audio buffer → Voice System
3. Wake word detection → Porcupine
4. If triggered → Whisper STT → Text
5. Speaker verification → Resemblyzer → Verified/Rejected
6. Text → Server Bridge → HTTP POST
7. ATOM receives → Flask Client Bridge
8. Room Manager → Get context
9. Librarian → Search relevant memories
10. LLM Interface → Generate response
11. Response → HTTP back to desktop
12. Desktop → TTS → Speaker
```

### Network Failure Path:

```
1. Server Bridge attempts ATOM
2. Timeout after 30s
3. Retry 3 times (exponential backoff)
4. If all fail → Network Fallback
5. Queue request for later
6. Use Small LLM on RTX 4070
7. Generate local response
8. When ATOM returns → Sync queue
```

---

## Configuration Architecture

### Client Brain Configs:

```
01_Client_Brain/config/
├── gpu_config.json              - GPU device assignments
├── network_config.json          - ATOM connection settings
├── voice_config.json            - Voice system settings
├── room_contexts.json           - Room definitions
├── automation_config.json       - Automation settings
├── audio_config.json            - Audio device settings
├── system_tray_config.json      - Tray icon settings
├── startup_config.json          - Startup behavior
├── voice_profile_config.json    - Speaker verification
└── wake_word_config.json        - Wake word settings
```

### Server Brain Configs:

```
02_Server_Brain/config/
├── server_config.json           - Flask server settings
├── llm_config.json              - Ollama configuration
├── librarian_config.json        - Vector DB settings
├── compression_strategy.json    - Memory compression rules
└── room_contexts.json           - Room configurations (synced)
```

---

## GPU Resource Allocation

### Desktop:

**RTX 5070 (Primary Voice GPU):**
- Faster-Whisper: ~4GB
- Kokoro TTS: ~2GB
- Headroom: ~2GB
- **Total:** 8GB

**RTX 4070 (Fallback LLM):**
- qwen2.5:7b: ~4GB
- Headroom: ~4GB
- **Total:** 8GB

### ATOM Server:

**Blackwell GB10:**
- qwen2.5:14b: ~8GB
- qwen2.5:70b: ~40GB (optional)
- FAISS: ~1GB
- Headroom: ~50-100GB
- **Total:** 128GB+

---

## Network Architecture

### Local Network (Primary):

```
Desktop ←───LAN───→ ATOM
   │                  │
   └──── Port 5000 ───┘
        HTTP/JSON
```

### Tailscale VPN (Remote):

```
Desktop ←───Tailscale───→ ATOM
100.x.x.1               100.x.x.2
   │                       │
   └───── Port 5000 ───────┘
         HTTP/JSON
```

**Advantages:**
- Secure encrypted tunnel
- Works anywhere (truck, away from home)
- No port forwarding needed
- NAT traversal automatic

---

## Security Model

### Authentication:
- Speaker verification (Resemblyzer embeddings)
- Similarity threshold: 0.65 default
- Can be disabled for convenience

### Network Security:
- No internet exposure (LAN or Tailscale only)
- Flask CORS limited to localhost/Tailscale IPs
- Windows Firewall: Block public networks
- UFW on ATOM: Allow only Tailscale subnet

### Automation Safety:
- Console window blacklist
- Emergency undo buffer
- Panic stop hotkey
- Action logging

### Data Privacy:
- All processing local (desktop + ATOM)
- No cloud services (except optional Tailscale)
- Logs stored locally
- No telemetry

---

## Failure Modes & Recovery

### ATOM Server Down:
- Desktop detects timeout
- Switches to RTX 4070 local LLM
- Queues requests for sync
- Continues limited operation

### GPU Failure:
- OOM errors → CPU fallback
- Temperature critical → Throttle
- Device error → Switch to backup GPU

### Network Congestion:
- Timeout → Retry with backoff
- High latency → Warn user
- Complete failure → Offline mode

### Microphone Failure:
- Error detection → Notify user
- System tray icon → Red
- Attempt device reinitialization

### Critical Error:
- Emergency stop triggered
- State saved to checkpoint
- All processes terminated
- Recovery script generated

---

## Performance Characteristics

### Voice System:
- Wake word: <100ms latency
- STT (Whisper): 500-1500ms per utterance
- Speaker verification: <100ms
- TTS (Kokoro): 200-800ms per sentence

### LLM Inference (ATOM):
- qwen2.5:14b: 20-50 tokens/sec
- qwen2.5:70b: 5-15 tokens/sec
- First token latency: 500-1000ms
- Context: 32K tokens

### Network:
- Local LAN: <10ms latency
- Tailscale: 20-100ms latency
- Bandwidth: 1-10 MB/s

### Total User Experience:
- Wake→Response: 2-5 seconds
- Simple queries: 2-3 seconds
- Complex queries: 5-10 seconds

---

## Scalability Considerations

### Adding More Rooms:
- Edit `room_contexts.json`
- Define system prompt
- Set temperature/model
- No code changes needed

### Supporting More Users:
- Record additional voice profiles
- Store embeddings in `voice_profiles/`
- System verifies against all profiles

### Larger Models:
- Install via Ollama: `ollama pull model:size`
- Update room configs to use new model
- Ensure GPU VRAM sufficient

### Multiple Clients:
- Flask supports concurrent requests
- Each client gets own session
- Room context per session
- Shared memory/librarian

---

## Monitoring & Maintenance

### Health Monitoring:
- GPU metrics every 30s
- Network ping to ATOM
- CSV logs in `logs/health_metrics.csv`

### Performance Profiling:
- Task timing with context managers
- CSV logs in `logs/performance_metrics.csv`
- Analyze bottlenecks

### Memory Compression:
- Automatic daily (2am PST)
- Manual: `python compression_system.py`
- Backup before compression

### Log Rotation:
- Manual: Delete old logs in `logs/`
- Recommend: Weekly cleanup
- Keep last 7 days minimum

---

## Development & Extension

### Adding New Voice Commands:
1. Update room system prompt
2. LLM naturally handles new requests
3. No code changes needed

### Adding New Automation:
1. Extend `automation.py`
2. Add new PyAutoGUI functions
3. Update undo buffer logic

### Adding New Rooms:
1. Edit `room_contexts.json`
2. Define behavior and model
3. Restart system

### Integrating External Services:
1. Add API client in new module
2. Call from LLM or automation
3. Handle errors gracefully

---

## Technology Stack

### Desktop (Windows):
- Python 3.10+
- PyTorch with CUDA 12.1
- Faster-Whisper (Whisper Large v3 Turbo)
- Resemblyzer (voice embeddings)
- Kokoro TTS
- Porcupine (wake word)
- PyAutoGUI (automation)
- Pystray (system tray)

### Server (Linux):
- Python 3.10+
- Ollama (LLM server)
- Flask (HTTP server)
- FAISS (vector database)
- Sentence-Transformers (embeddings)
- Pydantic (validation)
- PyNVML (GPU monitoring)

### Network:
- HTTP/JSON (application protocol)
- Tailscale (optional VPN)

---

## File Structure

```
VALCORE1/
├── 01_Client_Brain/          - Desktop components
│   ├── core/                 - Main modules
│   ├── config/               - Configuration files
│   ├── models/               - AI models
│   ├── voice_profiles/       - Speaker embeddings
│   └── main_client.py        - Entry point
│
├── 02_Server_Brain/          - ATOM components
│   ├── core/                 - Main modules
│   ├── config/               - Configuration files
│   ├── data/                 - Vector DB, memories
│   └── main_server.py        - Entry point
│
├── 03_Shared/                - Common utilities
│   ├── network_protocol.py   - Message schemas
│   ├── common_utils.py       - Utilities
│   └── performance_profiler.py
│
├── 04_Documentation/         - User guides
├── 05_Setup_Scripts/         - Installation scripts
├── 06_Deployment/            - Deployment tools
├── 07_Val_Protocols/         - Setup assistant guides
│
├── logs/                     - System logs
├── requirements.txt          - Python dependencies
└── START_VALCORE1.bat        - Windows launcher
```

---

## Design Philosophy

1. **Simplicity:** User-friendly for non-programmers
2. **Reliability:** Graceful degradation, fallbacks
3. **Privacy:** All processing local/on-premises
4. **Performance:** Optimize for low latency
5. **Flexibility:** Easy to extend and customize
6. **Safety:** Emergency stops, undo buffers
7. **Transparency:** Clear logs, status indicators

---

*VALCORE1 Architecture*
*Distributed AI Voice Assistant*
*Version 1.0 - November 2025*

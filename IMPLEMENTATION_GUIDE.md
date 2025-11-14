# VALCORE1 Implementation Guide

## Purpose
This guide explains what has been created and provides detailed specifications for completing the remaining ~75% of the VALCORE1 system.

## What You'll Find Here
1. Complete list of files that need to be created
2. Detailed specifications for each component
3. Code templates and examples
4. Integration points between components
5. Testing and validation procedures

---

## Current Status

### ✅ Created (25% Complete)
- Complete directory structure
- All configuration JSON files with schemas
- Core Client Brain modules (4 of 8):
  - `voice_system_unified.py` - Full implementation
  - `server_bridge.py` - Full implementation
  - `small_llm_interface.py` - Full implementation
  - `automation.py` - Full implementation
- Requirements files (client + server)
- Main entry point (`main_client.py`)
- Startup script (`START_VALCORE1.bat`)
- Ollama installation script

### ❌ Needs Implementation (75% Remaining)

---

## 1. Client Brain Modules (4 remaining)

### 1.1 system_tray.py
**Location:** `VALCORE1/01_Client_Brain/core/system_tray.py`

**Purpose:** Windows system tray icon with menu

**Requirements:**
- Use `pystray` library
- Icon shows status: green (listening), yellow (processing), red (error)
- Left-click: toggle microphone
- Right-click menu:
  - Mic On/Off
  - Status (show server connection, active room)
  - Settings
  - Exit
- Non-blocking (runs in separate thread)

**Key Methods:**
```python
class SystemTray:
    def __init__(self, voice_system, server_bridge, health_monitor)
    def start()  # Start tray in background thread
    def stop()   # Cleanup
    def update_status(status: str)  # Update icon color
    def show_menu()  # Display context menu
```

**Integration Points:**
- Import in `main_client.py`
- Pass references to voice_system, server_bridge, health_monitor
- Update icon based on system state

---

### 1.2 health_monitor.py
**Location:** `VALCORE1/01_Client_Brain/core/health_monitor.py`

**Purpose:** Monitor GPU temperature, RAM, disk, network latency

**Requirements:**
- Use `pynvml` for GPU metrics
- Use `psutil` for RAM/disk
- Ping ATOM server every 30s for latency
- Non-blocking notifications for warnings
- Log metrics to CSV: `logs/health_metrics.csv`

**Key Methods:**
```python
class HealthMonitor:
    def __init__(self, config_path: str)
    def start_monitoring()  # Start background thread
    def stop_monitoring()   # Stop thread
    def get_gpu_temp(device_id: int) -> float
    def get_ram_usage() -> float  # Percentage
    def get_disk_space(drive: str) -> float  # GB free
    def ping_server() -> float  # Latency in ms
    def check_thresholds()  # Check all and notify if exceeded
```

**Thresholds (from settings.json):**
- GPU temp warning: 85°C
- GPU temp critical: 90°C
- RAM warning: 85%
- Disk warning: <10GB free

---

### 1.3 emergency_stop.py
**Location:** `VALCORE1/01_Client_Brain/core/emergency_stop.py`

**Purpose:** Panic hotkey and kill switch

**Requirements:**
- Hotkey: `Ctrl+Shift+Alt+V`
- Use `keyboard` library for global hotkey
- Save checkpoint before shutdown (current room, mic state, pending commands)
- Kill all VALCORE1 processes immediately
- Log emergency stop events
- Recovery script to resume from checkpoint

**Key Methods:**
```python
class EmergencyStop:
    def __init__(self)
    def save_checkpoint(reason: str)  # Save state to .state/checkpoint_{timestamp}.json
    def kill_all_valcore_processes()  # Kill all processes matching 'valcore' or 'voice_system'
    def trigger_shutdown()  # Main emergency stop handler
    def log_emergency_stop()  # Log to emergency.log
```

**Checkpoint Format:**
```json
{
  "timestamp": "2025-11-14T10:30:45",
  "reason": "emergency_stop",
  "active_room": "general",
  "pending_commands": [],
  "mic_state": "enabled"
}
```

---

### 1.4 network_fallback.py
**Location:** `VALCORE1/01_Client_Brain/core/network_fallback.py`

**Purpose:** Handle offline mode and sync when server returns

**Requirements:**
- Queue messages when server is unavailable
- Periodic health checks (every 30s)
- Auto-sync when server comes back online
- Conflict detection (server state vs local state)
- Manual conflict resolution via system tray menu

**Key Methods:**
```python
class NetworkFallbackManager:
    def __init__(self)
    def check_server_health() -> bool
    def send_to_server(message: Dict) -> Optional[Dict]  # Send with fallback
    def sync_offline_queue()  # Sync queued messages
    def _has_conflict(message: Dict) -> bool  # Detect conflicts
    def resolve_conflict(conflict: Dict, resolution: str)  # "keep_local", "keep_server", "merge"
    def notify_user_offline_mode()
    def notify_user_sync_started()
    def notify_user_sync_complete(synced: int, conflicts: int)
```

**Queue Message Format:**
```json
{
  "type": "conversation",
  "conversation_id": "uuid",
  "timestamp": "2025-11-14T10:30:45",
  "room": "general",
  "user_input": "...",
  "assistant_response": "...",
  "version": 1
}
```

---

## 2. Server Brain Modules (5 modules)

### 2.1 large_llm_interface.py
**Location:** `VALCORE1/02_Server_Brain/core/large_llm_interface.py`

**Purpose:** Interface to Ollama for large language models

**Requirements:**
- Use `ollama` Python library
- Support streaming responses (optional)
- Handle system prompts for rooms
- Context window management (32K tokens)
- Temperature control per room

**Key Methods:**
```python
class LargeLLM:
    def __init__(self, config_path: str)
    def generate(prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> str
    def stream_generate(prompt: str, ...) -> Generator[str, None, None]  # Optional
    def get_available_models() -> List[str]
    def check_model_loaded(model_name: str) -> bool
```

---

### 2.2 librarian.py
**Location:** `VALCORE1/02_Server_Brain/core/librarian.py`

**Purpose:** Semantic memory search with FAISS

**Requirements:**
- Use `sentence-transformers` for embeddings (all-MiniLM-L6-v2)
- Use `faiss` for vector store
- Cosine similarity threshold: >0.7 for relevance
- Store conversations in room-specific directories
- Support cross-room search

**Key Methods:**
```python
class Librarian:
    def __init__(self, library_path: str)
    def add_conversation(room: str, text: str, metadata: Dict)  # Add to vector DB
    def search(query: str, room: Optional[str] = None, max_results: int = 10) -> List[Dict]
    def get_room_context(room: str, last_n: int = 5) -> List[Dict]  # Recent context
    def build_index()  # Rebuild FAISS index
    def save_index()   # Persist to disk
    def load_index()   # Load from disk
```

**Storage Format:**
- Daily conversations: `Library/daily/{YYYY-MM-DD}.json`
- Room contexts: `Library/rooms/{room_name}/context.json`
- FAISS index: `Library/faiss_index.bin`
- Metadata: `Library/metadata.json`

---

### 2.3 memory_compression.py
**Location:** `VALCORE1/02_Server_Brain/core/memory_compression.py`

**Purpose:** Compress conversations daily/monthly/yearly

**Requirements:**
- Use `schedule` library for task scheduling
- Run daily at 2am PST
- Catch-up logic if missed (check on startup if last run >24h ago)
- Semantic importance scoring (high/medium/low)
- LLM-generated summaries
- Backup before compression

**Key Methods:**
```python
class MemoryCompressor:
    def __init__(self, config_path: str, librarian: Librarian)
    def start_scheduler()  # Start background scheduler
    def stop_scheduler()   # Stop scheduler
    def compress_daily_summary(date: datetime) -> Dict
    def compress_monthly_rollup(year: int, month: int) -> Dict
    def compress_yearly_archive(year: int) -> Dict
    def score_semantic_importance(text: str, category: str) -> float
    def rollback_compression(date: datetime) -> bool  # Restore from backup
```

**Compression Strategy (from compression_strategy.json):**
- Daily: 2000 tokens max, 1500 target
- Monthly: 5000 tokens max, 4000 target
- Yearly: 10000 tokens max, 8000 target
- Preserve categories: decisions, action items, errors, code changes
- Discard categories: greetings, duplicates, failed attempts

---

### 2.4 room_manager.py
**Location:** `VALCORE1/02_Server_Brain/core/room_manager.py`

**Purpose:** Manage room contexts and switching

**Requirements:**
- Load room configurations from `room_contexts.json`
- Track active room per client session
- Inject room-specific system prompts
- Maintain room-specific conversation history

**Key Methods:**
```python
class RoomManager:
    def __init__(self, config_path: str, librarian: Librarian)
    def get_active_room(session_id: str) -> str
    def switch_room(session_id: str, room_name: str)
    def get_room_config(room_name: str) -> Dict
    def get_room_context(room_name: str, max_history: int = 10) -> str
    def list_rooms() -> List[str]
    def create_room(name: str, config: Dict)  # Advanced: create custom rooms
```

---

### 2.5 client_bridge.py
**Location:** `VALCORE1/02_Server_Brain/core/client_bridge.py`

**Purpose:** Flask server to receive client requests

**Requirements:**
- Use Flask with CORS enabled
- Listen on 0.0.0.0:5000
- Routes:
  - `POST /api/process` - Process user input
  - `GET /api/health` - Health check
  - `POST /api/room/switch` - Switch rooms
  - `POST /api/search` - Search library
- Thread-safe (multiple clients)

**Key Routes:**
```python
@app.route('/api/process', methods=['POST'])
def process_request():
    # Receive: {session_id, room, user_input}
    # Return: {response, room, timestamp}

@app.route('/api/health', methods=['GET'])
def health_check():
    # Return: {status: "ok", model: "...", uptime: ...}

@app.route('/api/search', methods=['POST'])
def search_library():
    # Receive: {query, room, max_results}
    # Return: {results: [...]}
```

---

## 3. Shared Modules (3 modules)

### 3.1 network_protocol.py
**Location:** `VALCORE1/03_Shared/network_protocol.py`

**Purpose:** JSON message schema and validation

**Requirements:**
- Define message types: voice_input, llm_response, command, error, health_check
- Validation with `pydantic`
- Serialization/deserialization
- Event IDs for tracking

**Message Types:**
```python
class VoiceInputMessage(BaseModel):
    event_id: str
    timestamp: str
    source: str  # "client"
    type: str    # "voice_input"
    payload: Dict  # {text, room, speaker_verified}

class LLMResponseMessage(BaseModel):
    event_id: str
    timestamp: str
    source: str  # "server"
    type: str    # "llm_response"
    payload: Dict  # {response, model, latency_ms}
```

---

### 3.2 common_utils.py
**Location:** `VALCORE1/03_Shared/common_utils.py`

**Purpose:** Shared utility functions

**Functions:**
- `generate_event_id() -> str` - UUID generation
- `get_timestamp() -> str` - ISO format timestamp
- `load_json_config(path: str) -> Dict` - Load and validate JSON
- `save_json_config(path: str, data: Dict)` - Save JSON
- `sanitize_filename(name: str) -> str` - Remove invalid chars
- `calculate_token_count(text: str) -> int` - Approximate token count (4 chars = 1 token)

---

### 3.3 performance_profiler.py
**Location:** `VALCORE1/03_Shared/performance_profiler.py`

**Purpose:** Track latency and performance metrics

**Requirements:**
- Context manager for timing code blocks
- CSV logging: `logs/performance.csv`
- Metrics: voice→text, text→LLM, LLM→response, total round-trip
- GPU utilization tracking
- Memory footprint

**Usage:**
```python
profiler = PerformanceProfiler()

with profiler.measure("voice_to_text"):
    text = voice.transcribe(audio)

with profiler.measure("llm_inference"):
    response = llm.generate(text)

profiler.save_metrics()
```

**CSV Format:**
```
timestamp,task,latency_ms,gpu_util_%,ram_mb
2025-11-14T10:30:45,voice_to_text,285,45,2048
2025-11-14T10:30:46,llm_inference,1250,92,8192
```

---

## 4. PowerShell Scripts (23 scripts)

### 4.1 Diagnostic Scripts (5 scripts)
**Location:** `00_SETUP_ASSISTANT/03_SCRIPTS_FOR_BEN/diagnostics/`

**1_test_gpu.ps1:**
- Check `nvidia-smi` available
- Detect all GPUs (index, name, memory)
- Verify CUDA available via PyTorch
- Check driver version
- Output: GPU list, CUDA status, driver version

**2_test_cuda.ps1:**
- Test CUDA Toolkit installation
- Check `nvcc --version`
- Verify CUDA libraries accessible
- Output: CUDA version, toolkit path

**3_test_microphone.ps1:**
- List all recording devices (Windows API)
- Show default input device
- Test PyAudio device detection
- Record 3s test audio
- Analyze amplitude (max/avg)
- Output: Device list, recording test results

**4_test_network_atom.ps1:**
- Ping ATOM server (192.168.1.121)
- Test port 11434 connectivity
- Check Ollama API response
- Measure latency
- Output: Ping time, port status, API health

**5_test_python_env.ps1:**
- Check Python version (3.10+)
- Test `pip` available
- Check virtual environment
- Test all critical imports (torch, faster-whisper, etc.)
- Output: Python version, import test results

---

### 4.2 Windows Setup Scripts (4 scripts)
**Location:** `00_SETUP_ASSISTANT/03_SCRIPTS_FOR_BEN/windows_setup/`

**1_install_startup.ps1:**
- Create scheduled task for VALCORE1
- Set to run at logon with highest privileges
- Target: `START_VALCORE1.bat`
- Output: Task creation status

**2_create_system_tray.ps1:**
- Verify `pystray` installed
- Test system tray icon creation
- Output: Tray test result

**3_configure_firewall.ps1:**
- Add Windows Firewall rule for port 11434 (Ollama)
- Add rule for Python.exe (VALCORE1)
- Output: Firewall rules created

**4_set_audio_defaults.ps1:**
- Set default microphone device
- Adjust input volume
- Disable audio enhancements
- Output: Audio config status

---

### 4.3 Voice Enrollment Scripts (4 scripts)
**Location:** `00_SETUP_ASSISTANT/03_SCRIPTS_FOR_BEN/voice_enrollment/`

**1_record_wake_word.ps1:**
- Record 10 samples of "Hey Val"
- 2 seconds each
- Save to `config/wake_word_samples/`
- Output: Sample quality check

**2_record_voice_profile.ps1:**
- Load 100 training phrases from `training_phrases.txt`
- Record each phrase (5 seconds)
- Save to `config/voice_profile_samples/`
- Output: Recording progress

**3_generate_embeddings.py:**
- Load voice profile samples
- Use Resemblyzer to generate embeddings
- Average embeddings into single profile
- Save to `config/voice_profiles/ben_voice.npy`
- Output: Embedding generation status

**4_test_recognition.ps1:**
- Test wake word detection (10 trials)
- Test speaker verification (10 trials)
- Calculate success rate
- Output: Recognition accuracy

---

### 4.4 Testing Scripts (10 scripts)
**Location:** `00_SETUP_ASSISTANT/03_SCRIPTS_FOR_BEN/testing/`

**test_gpu_detection.ps1** - Verify GPU detection
**test_microphone.ps1** - Test mic input
**test_wake_word.ps1** - Test "Hey Val" detection
**test_stt.ps1** - Test Faster-Whisper transcription
**test_tts.ps1** - Test Kokoro TTS output
**test_server_connection.ps1** - Test ATOM connectivity
**test_llm.ps1** - Test LLM inference (local + server)
**test_automation.ps1** - Test PyAutoGUI typing
**test_librarian.ps1** - Test semantic search
**test_emergency_stop.ps1** - Test panic hotkey

**run_all_tests.ps1** - Run all 10 tests sequentially and generate report

---

## 5. Protocol Documents (6 documents)

### 5.1 For Val (Sonnet 4.5)
**Location:** `00_SETUP_ASSISTANT/01_FOR_VAL_SONNET/`

**PHASE2_MASTER_PROTOCOL.md:**
- Complete step-by-step guide for Val to guide Ben
- 4 stages: Hardware diagnostics, Windows integration, Voice enrollment, First run
- For each stage: scripts to run, expected outputs, troubleshooting
- Error logging format
- Handoff template to Claude CLI

**HARDWARE_DIAGNOSTICS.md:**
- How to interpret GPU test outputs
- Common issues and fixes
- GPU device ID mismatch handling

**WINDOWS_INTEGRATION.md:**
- Startup service configuration
- System tray verification
- Firewall rule validation

**VOICE_ENROLLMENT.md:**
- Recording environment requirements
- Sample quality assessment
- Embedding generation process

**ERROR_RESPONSES.md:**
- Common error messages
- Ben-friendly explanations
- Fix procedures

**HANDOFF_TO_CLI.md:**
- Diagnostic results template
- Code fixes needed format
- Voice enrollment status
- Windows integration checklist

---

### 5.2 For Claude CLI
**Location:** `00_SETUP_ASSISTANT/02_FOR_CLAUDE_CLI/`

**PHASE3_VALIDATION.md:**
- Receive handoff from Val
- Apply code fixes
- Install dependencies
- Run test suite
- Validate configuration files
- Package for deployment
- Generate deployment report

**DEPENDENCY_INSTALL.md:**
- Install requirements in container
- Verify all imports
- Check CUDA availability

**CODE_FIXES.md:**
- How to apply fixes from Val's diagnostics
- File regeneration procedures
- Configuration updates

**FINAL_TESTS.md:**
- Unit test execution
- Integration test procedures
- End-to-end validation

---

## 6. MCP Tools Registry (5 servers + registry)

### 6.1 Filesystem MCP
**Location:** `04_Tools_Registry/mcp_servers/filesystem_mcp/`

**manifest.json:**
```json
{
  "name": "filesystem_mcp",
  "version": "1.0.0",
  "description": "Access files on A:\\ drive",
  "functions": [
    {"name": "read_file", "parameters": {"path": "string"}},
    {"name": "write_file", "parameters": {"path": "string", "content": "string"}},
    {"name": "list_directory", "parameters": {"path": "string"}},
    {"name": "search_files", "parameters": {"query": "string"}}
  ],
  "requires_auth": false
}
```

### 6.2 Google Drive MCP
**manifest.json:**
```json
{
  "name": "google_drive_mcp",
  "version": "1.0.0",
  "description": "Search and fetch Google Drive documents",
  "functions": [
    {"name": "search_drive", "parameters": {"query": "string", "max_results": "integer"}},
    {"name": "get_file", "parameters": {"file_id": "string"}},
    {"name": "create_file", "parameters": {"name": "string", "content": "string"}}
  ],
  "requires_auth": true,
  "auth_type": "oauth2"
}
```

### 6.3 Gmail MCP
Similar structure for email operations

### 6.4 Google Calendar MCP
Similar structure for calendar operations

### 6.5 Web Search MCP
Similar structure for web search

### 6.6 Tool Discovery
**Location:** `04_Tools_Registry/tool_discovery.py`

**Purpose:** Scan and register available MCP servers

```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.scan_mcp_servers()

    def scan_mcp_servers(self):
        # Read all manifest.json files
        # Register tools
        # Enable voice commands: "Hey Val, what tools do I have?"
```

---

## 7. Deployment Scripts (3 scripts)

### 7.1 Tailscale Setup
**Location:** `06_Deployment/`

**tailscale_setup.ps1** (Windows):
- Install Tailscale via `winget`
- Login to tailnet
- Get ATOM's Tailscale IP
- Update `network_config.json`

**tailscale_setup.sh** (Linux):
- Install Tailscale on ATOM
- Configure firewall for Ollama (port 11434)
- Display Tailscale IP

### 7.2 Windows Permissions
**windows_permissions.ps1:**
- Configure UAC elevation
- Add Windows Defender exclusions
- Set microphone privacy permissions
- Configure firewall rules
- Verify all settings

---

## 8. Documentation (5 documents)

### 8.1 SETUP_GUIDE.md
**Location:** `05_Documentation/`
- Complete setup instructions
- Prerequisites
- Installation steps
- Configuration
- First run
- Troubleshooting

### 8.2 VOICE_COMMANDS.md
- System control commands
- Room management
- Computer control
- Information queries
- Examples and use cases

### 8.3 TROUBLESHOOTING.md
- Common issues and solutions
- GPU problems
- Network connectivity
- Voice system issues
- LLM errors
- Diagnostic procedures

### 8.4 GPU_OPTIMIZATION.md
- GPU allocation strategy
- VRAM management
- Performance tuning
- Batch size optimization
- Temperature monitoring

### 8.5 REMOTE_ACCESS.md
- Tailscale setup guide
- Mobile access (Enchanted app)
- Network troubleshooting
- Security considerations

---

## 9. START_HERE.txt
**Location:** Root directory

Simple text file for Ben with first steps:
1. Extract location
2. Read 00_SETUP_ASSISTANT/00_READ_ME_FIRST.md
3. Contact Val (Sonnet 4.5)
4. Upload PHASE2_MASTER_PROTOCOL.md to Val
5. Follow Val's instructions

---

## Testing Strategy

### Unit Tests
Each module should have tests in `tests/` directory:
- `01_Client_Brain/tests/test_voice_system.py`
- `01_Client_Brain/tests/test_server_bridge.py`
- etc.

### Integration Tests
Test interactions between components:
- Voice → Server → Response
- Offline queue → Sync
- Room switching
- Emergency stop

### End-to-End Tests
Full system validation:
1. Start VALCORE1
2. Say "Hey Val"
3. Give command
4. Verify response
5. Test fallback (disconnect server)
6. Test emergency stop

---

## Estimated Completion Time

**By Component:**
- Client Brain modules (4): ~8 hours
- Server Brain modules (5): ~12 hours
- Shared modules (3): ~4 hours
- PowerShell scripts (23): ~12 hours
- Protocol documents (6): ~6 hours
- MCP Tools (6): ~8 hours
- Deployment scripts (3): ~3 hours
- Documentation (5): ~4 hours
- Testing suite: ~6 hours
- Integration & debugging: ~10 hours

**Total Estimate: ~73 hours of development work**

---

## Priority Order

### Phase 1 (MVP - Voice System Only)
1. Complete Client Brain modules (system_tray, health_monitor, emergency_stop, network_fallback)
2. Create diagnostic PowerShell scripts
3. Test voice system end-to-end
4. **Result:** Ben can use voice system with server fallback

### Phase 2 (Server Integration)
1. Complete Server Brain modules
2. Create server deployment scripts
3. Test client-server communication
4. **Result:** Full LLM capabilities with memory

### Phase 3 (Setup Assistance)
1. Create Val's protocol documents
2. Create all PowerShell setup scripts
3. Test with simulated Ben setup
4. **Result:** Val can guide Ben through setup

### Phase 4 (Polish)
1. Create all documentation
2. Implement MCP tools
3. Create Tailscale scripts
4. Full testing suite
5. **Result:** Production-ready system

---

## Development Environment Setup

### For Claude CLI
```bash
cd /path/to/ValCore1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r VALCORE1/01_Client_Brain/setup/requirements_client.txt
pip install -r VALCORE1/02_Server_Brain/setup/requirements_server.txt

# Install dev dependencies
pip install pytest black flake8 mypy
```

### Running Tests
```bash
pytest VALCORE1/01_Client_Brain/tests/
pytest VALCORE1/02_Server_Brain/tests/
pytest VALCORE1/03_Shared/tests/
```

### Code Quality
```bash
black VALCORE1/  # Format code
flake8 VALCORE1/  # Lint
mypy VALCORE1/  # Type check
```

---

## Questions to Resolve

1. **Voice Training:** Should we use the 100-phrase training set or simplify to 20 phrases?
2. **MCP Tools:** Should these be real implementations or placeholders for now?
3. **Testing:** Should tests be created before or after implementation?
4. **Documentation:** Should documentation be written as code is created or at the end?
5. **Val Protocol:** Should this be created first to guide the implementation?

---

## Next Steps

### Option A: Continue Implementation (Recommended)
Claude CLI continues implementing components in priority order

### Option B: Create Val Protocol First
Focus on creating complete Val protocol documents so Val can start guiding Ben

### Option C: Hybrid Approach
1. Create Val's protocol documents
2. Implement components Val needs for diagnostics
3. Test with Val guiding a simulated setup
4. Complete remaining components

---

## Support Resources

- Original specification: See the 3 instruction files provided
- Configuration examples: All in `config/` directories
- Code templates: See existing modules for patterns
- PowerShell examples: See provided scripts

---

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Status:** Ready for implementation

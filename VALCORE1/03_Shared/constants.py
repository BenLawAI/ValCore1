"""
VALCORE1 System Constants
Centralized configuration constants to eliminate magic numbers
"""

# ============================================================================
# AUDIO CONFIGURATION
# ============================================================================
DEFAULT_SAMPLE_RATE = 16000  # Hz - Standard for speech recognition
DEFAULT_CHUNK_SIZE = 1024  # Audio buffer size
DEFAULT_CHANNELS = 1  # Mono audio
COMMAND_RECORD_DURATION_SEC = 5  # Seconds to record after wake word
WAKE_WORD_SENSITIVITY = 0.7  # 0.0-1.0, higher = more sensitive

# ============================================================================
# SPEECH-TO-TEXT (FASTER-WHISPER)
# ============================================================================
DEFAULT_STT_MODEL = "large-v3-turbo"  # Balance of speed and accuracy
STT_BEAM_SIZE = 5  # Beam search width
STT_COMPUTE_TYPE = "float16"  # GPU precision
STT_VAD_FILTER = True  # Voice activity detection

# ============================================================================
# TEXT-TO-SPEECH (KOKORO)
# ============================================================================
DEFAULT_TTS_MODEL = "kokoro-v0_19"
TTS_SAMPLE_RATE = 24000  # Hz
TTS_SPEED = 1.0  # Speech rate multiplier

# ============================================================================
# SPEAKER VERIFICATION (RESEMBLYZER)
# ============================================================================
SPEAKER_VERIFICATION_THRESHOLD = 0.7  # Cosine similarity threshold
SPEAKER_VERIFICATION_FAIL_CLOSED = True  # Fail securely on errors

# ============================================================================
# NETWORK CONFIGURATION
# ============================================================================
DEFAULT_SERVER_TIMEOUT_SEC = 30  # HTTP request timeout
MAX_RETRY_ATTEMPTS = 3  # Server connection retries
RETRY_BACKOFF_BASE = 2  # Exponential backoff base
MAX_BACKOFF_SEC = 30  # Cap for exponential backoff
HEALTH_CHECK_INTERVAL_SEC = 30  # Server health check frequency

# Network retry jitter (prevents thundering herd)
RETRY_JITTER_MIN_SEC = 0.1
RETRY_JITTER_MAX_SEC = 1.0

# ============================================================================
# LLM CONFIGURATION
# ============================================================================
DEFAULT_LLM_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 2000
DEFAULT_CONTEXT_WINDOW = 32000  # Tokens
LLM_REQUEST_TIMEOUT_SEC = 60  # Generous timeout for generation

# Room-specific temperatures
ROOM_TEMP_GENERAL = 0.7  # Creative
ROOM_TEMP_TRUCK = 0.5  # Focused
ROOM_TEMP_INVOICE = 0.3  # Precise
ROOM_TEMP_LEGAL = 0.3  # Conservative

# ============================================================================
# AUTOMATION CONFIGURATION
# ============================================================================
TYPING_INTERVAL_SEC = 0.02  # Delay between keystrokes
UNDO_BUFFER_SIZE = 3  # Number of actions to remember
AUTOMATION_FAILSAFE = True  # PyAutoGUI failsafe (move mouse to corner)
AUTOMATION_PAUSE_SEC = 0.1  # Pause between PyAutoGUI commands

# Allowed applications for launch command (security whitelist)
ALLOWED_APPLICATIONS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "vscode": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "explorer": "explorer.exe",
}

# Blocked window types (never automate these)
BLOCKED_WINDOW_KEYWORDS = [
    "powershell",
    "cmd",
    "terminal",
    "console",
    "administrator",
    "bash",
    "ssh",
]

# ============================================================================
# GPU CONFIGURATION
# ============================================================================
GPU_0_DEVICE_ID = 0  # RTX 5070 - Voice system (STT, TTS, Wake Word)
GPU_1_DEVICE_ID = 1  # RTX 4070 - Fallback LLM

# GPU monitoring thresholds
GPU_TEMP_WARNING_C = 85  # Celsius
GPU_TEMP_CRITICAL_C = 90  # Celsius
GPU_MEMORY_WARNING_PERCENT = 90  # VRAM usage

# ============================================================================
# SYSTEM HEALTH MONITORING
# ============================================================================
RAM_WARNING_PERCENT = 85  # System RAM usage
DISK_WARNING_GB = 10  # Free space warning (GB)
NETWORK_LATENCY_WARNING_MS = 500  # High latency warning
NETWORK_LATENCY_CRITICAL_MS = 2000  # Critical latency

# Health check frequencies
HEALTH_MONITOR_INTERVAL_SEC = 60  # How often to check system health
HEALTH_LOG_INTERVAL_SEC = 300  # How often to log metrics (5 min)

# ============================================================================
# EMERGENCY STOP
# ============================================================================
EMERGENCY_HOTKEY = "ctrl+shift+alt+v"  # Panic key combination
CHECKPOINT_RETENTION_DAYS = 7  # Keep checkpoints for 7 days
SHUTDOWN_GRACE_PERIOD_SEC = 5  # Time to save state before kill

# ============================================================================
# OFFLINE/FALLBACK CONFIGURATION
# ============================================================================
OFFLINE_QUEUE_MAX_SIZE = 1000  # Max messages to queue offline
OFFLINE_SYNC_RETRY_INTERVAL_SEC = 300  # Try sync every 5 minutes
CONFLICT_DETECTION_ENABLED = True  # Check for conflicts during sync

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL_DEFAULT = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_MAX_SIZE_MB = 100  # Rotate logs at 100MB
LOG_BACKUP_COUNT = 5  # Keep 5 old log files
LOG_RETENTION_DAYS = 30  # Delete logs older than 30 days

# PII redaction patterns (for security)
PII_REDACTION_ENABLED = True
PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
    r"\b\d{16}\b",  # Credit card
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
]

# ============================================================================
# LIBRARY/MEMORY CONFIGURATION
# ============================================================================
# Memory compression strategy
DAILY_SUMMARY_MAX_TOKENS = 2000
DAILY_SUMMARY_TARGET_TOKENS = 1500
MONTHLY_SUMMARY_MAX_TOKENS = 5000
MONTHLY_SUMMARY_TARGET_TOKENS = 4000
YEARLY_SUMMARY_MAX_TOKENS = 10000
YEARLY_SUMMARY_TARGET_TOKENS = 8000

# Compression schedule (24-hour format, PST)
COMPRESSION_HOUR = 2  # 2 AM
COMPRESSION_MINUTE = 0

# Semantic search
FAISS_INDEX_TYPE = "L2"  # L2 distance for cosine similarity
SEMANTIC_SIMILARITY_THRESHOLD = 0.7  # Minimum relevance score
MAX_SEARCH_RESULTS = 10  # Default search result limit

# ============================================================================
# FILE PATHS (relative to VALCORE1 root)
# ============================================================================
CLIENT_CONFIG_DIR = "01_Client_Brain/config"
CLIENT_LOGS_DIR = "01_Client_Brain/logs"
SERVER_CONFIG_DIR = "02_Server_Brain/config"
SERVER_LOGS_DIR = "02_Server_Brain/logs"
LIBRARY_DIR = "../Library"  # Outside VALCORE1, persistent storage

# ============================================================================
# API/PROTOCOL CONFIGURATION
# ============================================================================
API_VERSION = "1.0"
MESSAGE_PROTOCOL_VERSION = "1.0"
MAX_MESSAGE_SIZE_KB = 512  # Max JSON message size

# Flask server (ATOM)
FLASK_HOST = "0.0.0.0"  # Listen on all interfaces
FLASK_PORT = 5000
FLASK_DEBUG = False  # Never enable in production
FLASK_THREADED = True  # Handle multiple clients

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================
REQUIRE_SPEAKER_VERIFICATION = False  # Enable after voice profile created
ENABLE_API_AUTHENTICATION = True  # Require API key for server requests
ENABLE_REQUEST_SIGNING = False  # Advanced: sign requests (future)
SECRETS_USE_KEYRING = True  # Store secrets in Windows Credential Manager

# Rate limiting
MAX_COMMANDS_PER_MINUTE = 30  # Prevent abuse
RATE_LIMIT_ENABLED = True

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================
# Thread pool sizes
WORKER_THREAD_POOL_SIZE = 4
IO_THREAD_POOL_SIZE = 8

# Request queue sizes
COMMAND_QUEUE_MAX_SIZE = 10
AUDIO_QUEUE_MAX_SIZE = 100

# Timeouts
COMPONENT_INIT_TIMEOUT_SEC = 30  # Max time for component initialization
GRACEFUL_SHUTDOWN_TIMEOUT_SEC = 10  # Max time for graceful shutdown

# ============================================================================
# FEATURE FLAGS (for gradual rollout)
# ============================================================================
FEATURE_SYSTEM_TRAY = True
FEATURE_SPEAKER_VERIFICATION = True
FEATURE_EMERGENCY_STOP = True
FEATURE_OFFLINE_QUEUE = True
FEATURE_MEMORY_COMPRESSION = True
FEATURE_MCP_TOOLS = False  # Not implemented yet
FEATURE_MULTIMODAL = False  # Future: vision capabilities

# ============================================================================
# VERSION INFORMATION
# ============================================================================
VALCORE_VERSION = "2.0.0"
VALCORE_CODENAME = "Production Ready"
VALCORE_BUILD_DATE = "2025-11-14"

# ============================================================================
# DEVELOPMENT/DEBUG
# ============================================================================
DEBUG_MODE = False  # Enable verbose logging and debug features
ENABLE_PROFILING = False  # Track performance metrics
MOCK_HARDWARE = False  # Use mocks for testing without GPU/mic

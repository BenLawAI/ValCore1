# Environment Variables Setup Guide

## Overview

ValCore1 now uses environment variables to store sensitive configuration like API keys. This prevents secrets from being committed to version control and makes deployment more secure.

## Quick Start

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file with your actual values:**
   ```bash
   # On Windows
   notepad .env

   # On Linux/Mac
   nano .env
   ```

3. **Required: Add your Picovoice API key:**
   ```bash
   PICOVOICE_ACCESS_KEY=your_actual_key_here
   ```

4. **The `.env` file is automatically ignored by git** - your secrets are safe!

## Required Environment Variables

### PICOVOICE_ACCESS_KEY (Required for Wake Word)
- **Purpose:** Wake word detection ("Hey Val")
- **Get it from:** https://console.picovoice.ai/
- **Example:** `PICOVOICE_ACCESS_KEY=AbCdEf123456...`

## Optional Environment Variables

### Network Configuration
- `ATOM_LOCAL_IP` - ATOM server local IP (default: 192.168.1.121)
- `ATOM_TAILSCALE_IP` - ATOM server Tailscale IP (optional)
- `PREFER_TAILSCALE` - Use Tailscale instead of local (true/false)

### API Security (Recommended)
- `VALCORE_API_KEY` - Secure API key for authentication
  - Generate one: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### LLM Configuration
- `OLLAMA_BASE_URL` - Ollama server URL (default: http://localhost:11434)
- `DEFAULT_LLM_MODEL` - Default model name (default: qwen2.5:14b)
- `FALLBACK_LLM_MODEL` - Client fallback model (default: qwen2.5:7b)

### Paths
- `LIBRARY_PATH` - Custom library path (default: /home/user/ValCore1/Library)
- `LOG_PATH` - Custom log directory (default: ./logs)

### Flask Server
- `FLASK_HOST` - Server bind address (default: 0.0.0.0)
- `FLASK_PORT` - Server port (default: 5000)
- `FLASK_DEBUG` - Enable debug mode (true/false)

## How It Works

ValCore1 loads configuration in this priority order:

1. **Environment variables** (highest priority)
2. **`.env` file** (loaded automatically)
3. **JSON config files** (default values)

This means:
- Set secrets in `.env` (safe, not committed)
- Keep defaults in JSON files (committed to git)
- Environment variables override JSON values

## Configuration Files That Use .env

### Client Brain
- `voice_config.json` - Uses `PICOVOICE_ACCESS_KEY`
- `network_config.json` - Uses `ATOM_LOCAL_IP`, `ATOM_TAILSCALE_IP`, `PREFER_TAILSCALE`

### Server Brain
- `settings.json` - Uses `OLLAMA_BASE_URL`, `DEFAULT_LLM_MODEL`, `LIBRARY_PATH`

## Security Best Practices

✅ **DO:**
- Keep your `.env` file private
- Use strong, random API keys
- Generate unique keys per environment
- Back up your `.env` file securely (NOT in git!)

❌ **DON'T:**
- Commit `.env` to git (it's already in .gitignore)
- Share your `.env` file publicly
- Hardcode secrets in JSON files
- Use weak or default API keys

## Troubleshooting

### "Porcupine access key not configured"
**Solution:** Add your key to `.env`:
```bash
PICOVOICE_ACCESS_KEY=your_key_here
```

### "python-dotenv not installed"
**Solution:** Install the dependency:
```bash
pip install python-dotenv
```

### "Environment variable not loading"
**Solution:**
1. Check that `.env` file exists in project root
2. Verify no typos in variable names
3. Restart the application after changes
4. Check file is not named `.env.txt` (no extension!)

### Changes not taking effect
**Solution:** Restart ValCore1 client/server after modifying `.env`

## Example `.env` File

```bash
# Copy from .env.example and fill in your values

# Required
PICOVOICE_ACCESS_KEY=AbCdEf123456789...

# Optional - Network
ATOM_LOCAL_IP=192.168.1.121
PREFER_TAILSCALE=false

# Optional - Security
VALCORE_API_KEY=your_secure_random_key_here

# Optional - Custom paths
LIBRARY_PATH=/home/user/ValCore1/Library
LOG_PATH=/home/user/ValCore1/logs
```

## Migration from Old Setup

If you previously had API keys in config files:

1. Create `.env` file from template
2. Copy your Picovoice key to `PICOVOICE_ACCESS_KEY` in `.env`
3. Remove the key from `voice_config.json` (leave it empty: `"access_key": ""`)
4. The system will automatically use the environment variable

## Production Deployment

For production environments:

1. **Don't copy `.env` file** - set environment variables directly
2. Use your system's secret management:
   - **Linux/Docker:** Set env vars in systemd service or docker-compose
   - **Windows Service:** Set in service configuration
   - **Cloud:** Use secret managers (AWS Secrets Manager, Azure Key Vault, etc.)

3. Example systemd service:
   ```ini
   [Service]
   Environment="PICOVOICE_ACCESS_KEY=your_key"
   Environment="VALCORE_API_KEY=your_api_key"
   ExecStart=/path/to/python /path/to/main_server.py
   ```

## Need Help?

- Check that `.env` is in the project root directory
- Verify environment variable names match exactly (case-sensitive)
- Look for warning messages in logs about .env loading
- See main documentation in `04_Documentation/` folder

---

**Security Note:** Never commit your `.env` file or share it publicly. Treat it like a password file!

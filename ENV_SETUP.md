# Environment Variable Setup

## Quick Start

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your values:
   ```bash
   nano .env  # or use your preferred editor
   ```

3. The `.env` file is automatically loaded when VALCORE1 starts

## Configuration Priority

VALCORE1 loads configuration in this order (later overrides earlier):

1. **Config files** (`config/*.json`) - Base configuration
2. **Environment variables** - Override specific values
3. **.env file** - Convenient way to set environment variables locally

## Using Environment Variables

### In Python Code

```python
from VALCORE1.03_Shared.config_loader import ConfigLoader

# Initialize (loads .env file)
ConfigLoader.load_env_file()

# Get individual values
api_key = ConfigLoader.get_env('OPENAI_API_KEY', required=True)
debug_mode = ConfigLoader.get_bool('DEBUG_MODE', default=False)
port = ConfigLoader.get_int('SERVER_PORT', default=5000)
allowed_origins = ConfigLoader.get_list('ALLOWED_CORS_ORIGINS')

# Load config file with environment overrides
config = ConfigLoader.load_config_with_env(
    'config/settings.json',
    env_prefix='VALCORE_'
)
```

### Environment Variable Naming

For nested config values, use underscore notation:

- `config['server']['host']` → `VALCORE_SERVER_HOST`
- `config['ollama']['base_url']` → `VALCORE_OLLAMA_BASE_URL`

## Security Best Practices

1. **NEVER** commit `.env` to version control
2. **ALWAYS** use strong, random values for secrets
3. **ROTATE** API keys and tokens regularly
4. **LIMIT** API key permissions to minimum required
5. **USE** different credentials for dev/staging/production

## Example: Adding External LLM APIs

To add support for OpenAI or Anthropic:

1. Add to `.env`:
   ```bash
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   ```

2. Use in code:
   ```python
   from config_loader import ConfigLoader

   openai_key = ConfigLoader.get_env('OPENAI_API_KEY')
   if openai_key:
       # Initialize OpenAI client
       pass
   ```

## Production Deployment

For production, set environment variables directly in your deployment platform:

- **Docker**: Use `--env-file` or `-e` flags
- **systemd**: Set in service unit file
- **Cloud**: Use platform's secret management (AWS Secrets Manager, etc.)

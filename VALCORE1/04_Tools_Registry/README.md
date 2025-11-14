# VALCORE1 Tools Registry - MCP Server Integration

This directory contains configurations for Model Context Protocol (MCP) servers that extend VALCORE1's capabilities.

## What are MCP Servers?

MCP (Model Context Protocol) servers are tools that allow VALCORE1 to interact with external systems:
- **Filesystem**: Read/write files on your computer
- **Google Drive**: Access Drive documents
- **Gmail**: Send/read emails
- **Calendar**: Manage events
- **Web Search**: Search the internet

## Available MCP Servers

### 1. Filesystem MCP
**Purpose:** Local file operations
- Read files
- Write files
- List directories
- Search files by content

**Status:** Configuration ready
**Setup:** See `filesystem/README.md`

### 2. Google Drive MCP
**Purpose:** Cloud storage integration
- Upload/download files
- Search documents
- Share files
- Manage folders

**Status:** Configuration ready (requires OAuth)
**Setup:** See `google_drive/README.md`

### 3. Gmail MCP
**Purpose:** Email management
- Send emails
- Read inbox
- Search messages
- Manage labels

**Status:** Configuration ready (requires OAuth)
**Setup:** See `gmail/README.md`

### 4. Calendar MCP
**Purpose:** Schedule management
- Create events
- View schedule
- Set reminders
- Manage multiple calendars

**Status:** Configuration ready (requires OAuth)
**Setup:** See `calendar/README.md`

### 5. Web Search MCP
**Purpose:** Internet search
- Search queries
- Get web content
- Extract information
- Research topics

**Status:** Configuration ready (requires API key)
**Setup:** See `web_search/README.md`

## Integration with VALCORE1

### How MCP Works with Voice Commands

**Example 1: File Operations**
```
You: "Hey Val, read my budget spreadsheet"
Val: Uses Filesystem MCP to locate and read the file
```

**Example 2: Email**
```
You: "Hey Val, send an email to John about the meeting"
Val: Uses Gmail MCP to compose and send email
```

**Example 3: Calendar**
```
You: "Hey Val, what's on my schedule tomorrow?"
Val: Uses Calendar MCP to retrieve events
```

## Setup Priority

**Recommended order:**
1. **Filesystem** (Essential) - No API keys needed
2. **Web Search** (Useful) - Requires API key
3. **Calendar** (Optional) - Requires Google OAuth
4. **Gmail** (Optional) - Requires Google OAuth
5. **Google Drive** (Optional) - Requires Google OAuth

## Security Considerations

### API Keys and Credentials
- Store in environment variables, NOT in config files
- Use `.env` file (add to `.gitignore`)
- Never commit credentials to git

### OAuth Tokens
- Stored in `~/.valcore1/tokens/`
- Encrypted at rest
- Expire after 1 hour (auto-refresh)

### Permissions
- MCP servers run with user permissions
- Cannot access files outside allowed directories
- Cannot perform system-level operations

## Configuration Format

Each MCP server has a `config.json`:

```json
{
  "name": "filesystem",
  "enabled": true,
  "priority": 1,
  "settings": {
    "allowed_directories": [
      "A:\\Documents",
      "A:\\Projects"
    ],
    "forbidden_paths": [
      "C:\\Windows",
      "C:\\Program Files"
    ]
  }
}
```

## Enabling/Disabling MCPs

### Enable an MCP
```json
{
  "enabled": true
}
```

### Disable an MCP
```json
{
  "enabled": false
}
```

### Priority (1-10)
Lower numbers = higher priority
- 1: Critical (filesystem)
- 5: Important (email, calendar)
- 10: Optional (web search)

## Usage in Voice Commands

VALCORE1 automatically selects the appropriate MCP based on your command:

**File operations → Filesystem MCP**
- "Read the file..."
- "Save this to..."
- "Find files containing..."

**Email → Gmail MCP**
- "Send an email..."
- "Check my inbox..."
- "Reply to the last message..."

**Schedule → Calendar MCP**
- "What's my schedule..."
- "Add a meeting..."
- "When is my next appointment..."

**Research → Web Search MCP**
- "Search for..."
- "Look up..."
- "Find information about..."

## Troubleshooting

### MCP not responding
1. Check `enabled: true` in config.json
2. Verify API keys/tokens are valid
3. Review logs in `04_Tools_Registry/logs/`

### Permission errors
1. Check `allowed_directories` includes target path
2. Ensure user has file system permissions
3. Run VALCORE1 with appropriate privileges

### OAuth expired
1. Delete old token: `~/.valcore1/tokens/[service].json`
2. Restart VALCORE1
3. Complete OAuth flow again

## Advanced Configuration

### Rate Limiting
Prevent API quota exhaustion:
```json
{
  "rate_limit": {
    "requests_per_minute": 60,
    "burst_limit": 10
  }
}
```

### Caching
Improve performance:
```json
{
  "cache": {
    "enabled": true,
    "ttl_seconds": 300,
    "max_size_mb": 50
  }
}
```

### Logging
Debug issues:
```json
{
  "logging": {
    "level": "INFO",
    "file": "logs/mcp_filesystem.log",
    "rotate": true
  }
}
```

## Future MCP Servers

**Potential additions:**
- Slack integration
- GitHub integration
- Database access
- Home automation (HomeAssistant)
- Task management (Todoist)

To request new MCPs, add to:
`04_Tools_Registry/requests/new_mcp_ideas.txt`

---

**Created by:** VALCORE1 Setup
**Date:** 2025-11-14
**Version:** 1.0

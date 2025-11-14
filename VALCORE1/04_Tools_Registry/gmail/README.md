# Gmail MCP Server

Gmail integration for email management with VALCORE1.

## Purpose

Allows VALCORE1 to send, read, and manage Gmail through voice commands.

## Setup

### 1. Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Create new project: "VALCORE1 Gmail"
3. Enable Gmail API:
   - APIs & Services → Library
   - Search "Gmail API"
   - Click Enable

### 2. Create OAuth Credentials

1. APIs & Services → Credentials
2. Create Credentials → OAuth client ID
3. Application type: Desktop app
4. Name: "VALCORE1 Desktop"
5. Download JSON credentials

### 3. Set Environment Variables

```powershell
# Extract from downloaded JSON
$creds = Get-Content -Path "path\to\credentials.json" | ConvertFrom-Json

# Set environment variables
[System.Environment]::SetEnvironmentVariable('GMAIL_CLIENT_ID', $creds.installed.client_id, 'User')
[System.Environment]::SetEnvironmentVariable('GMAIL_CLIENT_SECRET', $creds.installed.client_secret, 'User')
```

### 4. Enable in Config

Edit `config.json`:
```json
{
  "enabled": true
}
```

### 5. First Run - OAuth Flow

When you first use Gmail commands:
1. VALCORE1 will open browser
2. Sign in to your Google account
3. Grant permissions
4. Token saved to `~/.valcore1/tokens/gmail_token.json`
5. Future use is automatic!

## Voice Commands

### Reading Email

```
"Hey Val, check my inbox"
"Hey Val, read my latest emails"
"Hey Val, show unread messages"
"Hey Val, find emails from John"
"Hey Val, search emails about the project"
```

### Sending Email

```
"Hey Val, send an email to john@example.com"
Val: "What's the subject?"
You: "Meeting tomorrow"
Val: "What's the message?"
You: "Let's meet at 3pm to discuss the project"
Val: "Send it? Yes or no"
You: "Yes"
```

### Managing Email

```
"Hey Val, archive this email"
"Hey Val, mark as read"
"Hey Val, label this as Important"
"Hey Val, move to trash"
```

## Configuration Options

### Email Reading

```json
{
  "email_options": {
    "max_results": 50,          // How many emails to fetch
    "include_spam_trash": false, // Include spam/trash
    "mark_as_read": false       // Auto-mark as read
  }
}
```

### Sending Options

```json
{
  "send_options": {
    "default_signature": true,
    "signature_text": "\n\nSent via VALCORE1",
    "confirm_before_send": true,  // Always ask before sending
    "save_to_sent": true
  }
}
```

### Safety Settings

```json
{
  "safety": {
    "require_confirmation_for": [
      "delete",
      "archive",
      "send_to_multiple"
    ],
    "max_recipients": 10  // Prevent accidental mass emails
  }
}
```

## Security Best Practices

1. **Never disable confirm_before_send**
   - Prevents accidental emails
   - Gives you chance to review

2. **Keep max_recipients low**
   - Prevents mass email mistakes
   - Default: 10 recipients

3. **Don't log email content**
   - Privacy protection
   - `log_email_content: false`

4. **Token security**
   - Token stored in `~/.valcore1/tokens/`
   - Auto-refreshes every hour
   - Never commit tokens to git

5. **OAuth scopes**
   - Only grant necessary permissions
   - Can revoke at: https://myaccount.google.com/permissions

## Scopes Explained

```
gmail.readonly    - Read emails only
gmail.send        - Send emails
gmail.compose     - Draft emails
gmail.modify      - Modify labels, archive, delete
```

**Recommendation:** Start with `readonly` and `send` only.

## Troubleshooting

### "OAuth error: invalid_client"
- Client ID/secret not set correctly
- Environment variables missing

**Fix:** Verify environment variables:
```powershell
[System.Environment]::GetEnvironmentVariable('GMAIL_CLIENT_ID', 'User')
```

### "Token expired"
- OAuth token needs refresh
- Token file corrupted

**Fix:** Delete token and re-authenticate:
```powershell
Remove-Item $env:USERPROFILE\.valcore1\tokens\gmail_token.json
# Restart VALCORE1 to trigger new OAuth flow
```

### "Rate limit exceeded"
- Too many API calls
- Gmail quota hit

**Fix:** Wait a few minutes, reduce requests

### "Permission denied"
- Missing OAuth scope
- Account doesn't have access

**Fix:** Re-authenticate with correct scopes

## Privacy Considerations

### What Google Sees
- Your email content (for processing)
- API usage logs
- OAuth grant history

### What VALCORE1 Stores
- OAuth token (encrypted)
- Cached email metadata (optional)
- Logs (email content NOT logged by default)

### What's Sent to LLM
- Email content for processing commands
- Never sent to external servers
- Processed locally or on ATOM only

## Advanced Configuration

### Auto-Labeling
Automatically label emails processed by VALCORE1:
```json
{
  "email_options": {
    "auto_label": true,
    "label_name": "VALCORE1/Processed"
  }
}
```

### Smart Replies
Generate reply suggestions:
```json
{
  "smart_replies": {
    "enabled": true,
    "tone": "professional",
    "max_length": 200
  }
}
```

### Filters
Auto-process certain emails:
```json
{
  "filters": [
    {
      "from": "noreply@example.com",
      "action": "archive",
      "label": "Notifications"
    }
  ]
}
```

## Logs

Location: `04_Tools_Registry/logs/mcp_gmail.log`

Review logs to see:
- Email commands executed
- API call status
- OAuth refresh events
- Errors encountered

**Note:** Email content is NOT logged for privacy.

---

**Status:** ⚪ Requires Setup (OAuth)
**Priority:** 5 (Optional)
**API Keys:** OAuth credentials required
**Free Tier:** Yes (Gmail API quota: 1 billion requests/day)

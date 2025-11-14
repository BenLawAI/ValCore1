# Google Drive MCP Server

Google Drive integration for cloud file storage with VALCORE1.

## Purpose

Allows VALCORE1 to upload, download, and manage files on Google Drive through voice commands.

## Setup

### 1. Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Create new project: "VALCORE1 Drive"
3. Enable Google Drive API:
   - APIs & Services → Library
   - Search "Google Drive API"
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
[System.Environment]::SetEnvironmentVariable('GDRIVE_CLIENT_ID', $creds.installed.client_id, 'User')
[System.Environment]::SetEnvironmentVariable('GDRIVE_CLIENT_SECRET', $creds.installed.client_secret, 'User')
```

### 4. Enable in Config

Edit `config.json`:
```json
{
  "enabled": true
}
```

### 5. First Run - OAuth Flow

When you first use Drive commands:
1. VALCORE1 will open browser
2. Sign in to your Google account
3. Grant Drive permissions
4. Token saved to `~/.valcore1/tokens/gdrive_token.json`
5. Future use is automatic!

## Voice Commands

### Uploading Files

```
"Hey Val, upload this file to Drive"
"Hey Val, save this document to Drive"
"Hey Val, backup my notes to Google Drive"
```

### Downloading Files

```
"Hey Val, download my budget spreadsheet from Drive"
"Hey Val, get the project proposal from Drive"
"Hey Val, find and download meeting notes"
```

### Searching

```
"Hey Val, search Drive for invoices"
"Hey Val, find all PDFs in Drive"
"Hey Val, list recent Drive files"
```

### Managing Files

```
"Hey Val, share this Drive file with john@example.com"
"Hey Val, create a new folder in Drive called Projects"
"Hey Val, move this file to the Archive folder"
```

## Configuration Options

### File Size Limits

```json
{
  "file_options": {
    "max_file_size_mb": 100
  }
}
```

### Allowed File Types

```json
{
  "file_options": {
    "allowed_mime_types": [
      "application/pdf",
      "text/plain",
      "application/vnd.google-apps.document"
    ]
  }
}
```

### Google Docs Conversion

```json
{
  "file_options": {
    "convert_google_docs": true,  // Convert Docs to .docx
    "download_format": "original"
  }
}
```

### Upload Settings

```json
{
  "upload_options": {
    "default_folder": "VALCORE1",
    "create_folder_if_missing": true,
    "overwrite_existing": false
  }
}
```

## Scopes Explained

```
drive.file      - Access files created by VALCORE1
drive.readonly  - Read all files
drive           - Full Drive access (not recommended)
```

**Recommendation:** Use `drive.file` + `drive.readonly` for security.

## Security Best Practices

1. **Limited scopes**
   - Only grant necessary permissions
   - Avoid `drive` (full access) scope

2. **No auto-sharing**
   - `share_by_default: false`
   - Explicit sharing only

3. **No overwrites**
   - `overwrite_existing: false`
   - Prevents accidental data loss

4. **Token security**
   - Token stored in `~/.valcore1/tokens/`
   - Never commit to git
   - Revoke at: https://myaccount.google.com/permissions

## Troubleshooting

### "OAuth error: invalid_client"
- Client ID/secret not set correctly

**Fix:** Verify environment variables:
```powershell
[System.Environment]::GetEnvironmentVariable('GDRIVE_CLIENT_ID', 'User')
```

### "File too large"
- File exceeds max_file_size_mb

**Fix:** Increase limit or use different transfer method

### "Token expired"
- OAuth token needs refresh

**Fix:** Delete token and re-authenticate:
```powershell
Remove-Item $env:USERPROFILE\.valcore1\tokens\gdrive_token.json
```

### "Quota exceeded"
- Too many API calls
- Drive storage full

**Fix:** Wait a few minutes or check storage

## Advanced Configuration

### Automatic Backup

Upload files automatically:
```json
{
  "auto_backup": {
    "enabled": true,
    "folders": [
      "A:\\Documents\\Important"
    ],
    "schedule": "daily",
    "time": "02:00"
  }
}
```

### Smart Organization

Auto-organize by type:
```json
{
  "smart_folders": {
    "enabled": true,
    "pdf": "Documents/PDFs",
    "image": "Documents/Images",
    "spreadsheet": "Documents/Spreadsheets"
  }
}
```

### Shared Drives

Access team drives:
```json
{
  "search_options": {
    "search_shared_drives": true
  }
}
```

## Privacy Considerations

### What Google Sees
- Files you upload/download
- API usage logs
- OAuth grant history

### What VALCORE1 Stores
- OAuth token (encrypted)
- File metadata cache
- Operation logs

### What's Sent to LLM
- File content for processing
- Never sent to external servers
- Processed locally or on ATOM only

## Logs

Location: `04_Tools_Registry/logs/mcp_google_drive.log`

Review logs to see:
- File operations
- Upload/download status
- API errors
- Quota usage

---

**Status:** ⚪ Requires Setup (OAuth)
**Priority:** 7 (Optional)
**API Keys:** OAuth credentials required
**Free Tier:** 15 GB storage included with Google account

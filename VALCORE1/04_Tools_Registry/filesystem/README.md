# Filesystem MCP Server

Local filesystem access for VALCORE1.

## Purpose

Allows VALCORE1 to read and write files on your computer through voice commands.

## Setup

### 1. No API Keys Needed
Filesystem MCP works immediately - no configuration required!

### 2. Configure Allowed Directories (Optional)

Edit `config.json` to customize which directories VALCORE1 can access:

```json
{
  "allowed_directories": [
    "A:\\000_START_HERE",
    "A:\\Documents",
    "A:\\Projects"
  ]
}
```

### 3. Security Settings

**Forbidden Paths** (VALCORE1 cannot access):
- System directories (C:\Windows, C:\Program Files)
- Protected operating system files

**Allowed Operations**:
- ✅ Read files
- ✅ Write files
- ❌ Delete files (disabled for safety)
- ❌ Execute files (disabled for security)

## Voice Commands

### Reading Files

```
"Hey Val, read my notes.txt"
"Hey Val, what's in the budget spreadsheet?"
"Hey Val, show me the latest log file"
```

### Writing Files

```
"Hey Val, save this to meeting_notes.txt"
"Hey Val, create a new file called ideas.md"
"Hey Val, append this to my todo list"
```

### Searching Files

```
"Hey Val, find files containing 'invoice'"
"Hey Val, list all Python files in Projects"
"Hey Val, show me recent text files"
```

## Configuration Options

### File Size Limit
Default: 100 MB maximum per file
```json
{
  "max_file_size_mb": 100
}
```

### Allowed Extensions
Customize which file types can be accessed:
```json
{
  "allowed_extensions": [
    ".txt", ".md", ".json", ".py"
  ]
}
```

### Enable/Disable Operations
```json
{
  "operations": {
    "read": true,    // Read files
    "write": true,   // Write files
    "delete": false, // Delete files (keep disabled!)
    "execute": false // Execute files (keep disabled!)
  }
}
```

## Security Best Practices

1. **Never enable delete operations** unless absolutely necessary
2. **Never enable execute operations** for security
3. **Keep forbidden_paths** to protect system files
4. **Review allowed_directories** periodically
5. **Monitor logs** for unusual file access

## Troubleshooting

### "Permission denied"
- File is in a forbidden path
- Windows file permissions block access
- File is locked by another program

**Fix:** Check `config.json` allowed_directories

### "File too large"
- File exceeds max_file_size_mb

**Fix:** Increase limit in config.json or process file differently

### "Extension not allowed"
- File type not in allowed_extensions

**Fix:** Add extension to config.json

## Logs

Location: `04_Tools_Registry/logs/mcp_filesystem.log`

Review logs to see:
- Which files were accessed
- Any errors or permission issues
- Performance metrics

---

**Status:** ✅ Ready to use (no setup required)
**Priority:** 1 (Essential)
**API Keys:** None needed

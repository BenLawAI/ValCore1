# Google Drive Backup Setup for VALCORE1

**Goal:** Automatically backup VALCORE1 to Google Drive for safety

**Time Required:** 15-30 minutes (plus initial sync time)

---

## Why Backup to Google Drive?

- ✅ **Cloud Safety:** Your code is safe even if your PC crashes
- ✅ **Access Anywhere:** Download on any computer
- ✅ **Version History:** Google Drive keeps old versions
- ✅ **Free:** 15 GB free storage (enough for VALCORE1)
- ✅ **Automatic:** Syncs changes automatically

---

## Method 1: Google Drive Desktop (EASIEST - RECOMMENDED)

### Step 1: Install Google Drive Desktop

1. **Download the app:**
   - Go to: https://www.google.com/drive/download/
   - Click **"Download Drive for desktop"**
   - Click **"Download"** button

2. **Install the app:**
   - Run the downloaded file: `GoogleDriveSetup.exe`
   - Click **"Install"**
   - Wait for installation (1-2 minutes)

3. **Sign in:**
   - Google Drive will open automatically
   - Click **"Sign in with browser"**
   - Enter your Google email and password
   - Click **"Allow"** when asked for permissions

### Step 2: Set Up Folder Sync

1. **Open Google Drive settings:**
   - Look for Google Drive icon in system tray (bottom-right of screen)
   - Click the icon
   - Click the **gear/settings icon**
   - Click **"Preferences"**

2. **Add VALCORE1 folder:**
   - Click on **"My Laptop"** or **"My Computer"** tab
   - Click **"Add folder"** button
   - Navigate to `C:\VALCORE1`
   - Click **"Select Folder"**

3. **Choose sync option:**
   - Select **"Mirror files"** (recommended)
     - This keeps files on both your PC and Google Drive
   - OR select **"Stream files"**
     - This saves PC space but needs internet to access files
   - Click **"Done"**

4. **Start sync:**
   - Click **"Save"**
   - Google Drive will start uploading your files

### Step 3: Verify Backup

1. **Check sync status:**
   - Click Google Drive icon in system tray
   - Look for "Syncing..." or "All files synced"

2. **View in web browser:**
   - Go to: https://drive.google.com
   - You should see a "My Laptop" or "My Computer" folder
   - Inside, you should see "VALCORE1"

3. **What gets backed up:**
   - All Python code (`.py` files)
   - All PowerShell scripts (`.ps1` files)
   - All configuration files (`.json` files)
   - All documentation (`.md` files)
   - Your memories (Library folder)

4. **What does NOT get backed up (to save space):**
   - Virtual environment (`.venv` folder) - you can recreate this
   - Python cache files (`__pycache__` folders)
   - Temporary files

### Step 4: Optimize Your Backup

**To exclude large folders you don't need to backup:**

1. **Right-click on `.venv` folder**
2. **Select "Offline access" → "Available online only"**
3. This saves ~2 GB of Google Drive space

**To backup only important files:**

Create a new folder structure:

```
Google Drive/
└── VALCORE1_Backup/
    ├── Code/           ← Your Python and PowerShell files
    ├── Config/         ← Your configuration files
    ├── Docs/           ← Documentation
    └── Memories/       ← Library folder (your conversations)
```

---

## Method 2: Manual Backup (SIMPLE BUT MANUAL)

If you don't want to install the Google Drive app:

### Step 1: Compress VALCORE1

1. **Right-click on `C:\VALCORE1` folder**
2. **Select "Send to" → "Compressed (zipped) folder"**
3. **Name it:** `VALCORE1_Backup_2025-11-15.zip`
   - Use today's date so you know when you backed it up

### Step 2: Upload to Google Drive

1. **Go to:** https://drive.google.com
2. **Sign in** with your Google account
3. **Click "New"** button (top-left)
4. **Click "Folder"**
5. **Name it:** `VALCORE1_Backups`
6. **Click "Create"**
7. **Open the folder**
8. **Click "New" → "File upload"**
9. **Select your ZIP file:** `VALCORE1_Backup_2025-11-15.zip`
10. **Wait for upload** (15-30 minutes depending on internet speed)

### Step 3: Schedule Regular Backups

**Create a reminder to backup:**
- Weekly: Backup configuration files only (quick)
- Monthly: Full system backup (takes longer)
- Before major changes: Always backup first!

**Quick config backup:**
1. Compress only the `config` folders
2. Upload to Google Drive
3. Name it with the date

---

## Method 3: Command Line with Rclone (ADVANCED)

For automated backups via command line:

### Step 1: Install Rclone

1. **Download rclone:**
   - Go to: https://rclone.org/downloads/
   - Download the Windows version
   - Extract to: `C:\rclone\`

2. **Add to PATH:**
   ```powershell
   $env:Path += ";C:\rclone"
   ```

### Step 2: Configure Google Drive

1. **Run configuration:**
   ```powershell
   rclone config
   ```

2. **Follow prompts:**
   - Type `n` for new remote
   - Name: `gdrive`
   - Type: Choose `drive` (Google Drive)
   - Leave client_id and secret blank (press Enter)
   - Choose `1` for full access
   - Leave root_folder_id blank
   - Leave service_account_file blank
   - Choose `n` for advanced config
   - Choose `y` for auto config
   - Browser will open - sign in to Google
   - Choose `n` for team drive
   - Type `y` to confirm
   - Type `q` to quit

### Step 3: Create Backup Script

Create a file: `C:\VALCORE1\backup_to_drive.ps1`

```powershell
# VALCORE1 Backup Script
Write-Host "Starting VALCORE1 backup to Google Drive..." -ForegroundColor Cyan

# Exclude large folders
$exclude = "--exclude .venv/** --exclude **/__pycache__/** --exclude logs/**"

# Sync to Google Drive
rclone sync C:\VALCORE1 gdrive:VALCORE1_Backup $exclude --progress

Write-Host "Backup complete!" -ForegroundColor Green
```

### Step 4: Run Backup

```powershell
.\backup_to_drive.ps1
```

### Step 5: Schedule Automatic Backups

1. **Open Task Scheduler** (search in Start menu)
2. **Click "Create Basic Task"**
3. **Name:** "VALCORE1 Daily Backup"
4. **Trigger:** Daily
5. **Action:** Start a program
6. **Program:** `powershell.exe`
7. **Arguments:** `-File C:\VALCORE1\backup_to_drive.ps1`
8. **Finish**

---

## What to Backup

### Essential (Always backup):
- ✅ `VALCORE1/01_Client_Brain/` - Client code
- ✅ `VALCORE1/02_Server_Brain/` - Server code
- ✅ `VALCORE1/03_Shared/` - Shared utilities
- ✅ `VALCORE1/04_Documentation/` - Docs
- ✅ `VALCORE1/05_Setup_Scripts/` - Setup scripts
- ✅ `VALCORE1/01_Client_Brain/config/` - Your settings
- ✅ `Library/` - Your memories and conversations
- ✅ `pyproject.toml` - UV configuration
- ✅ `uv.lock` - Dependency versions
- ✅ `README.md` - Main documentation

### Optional (Can recreate):
- ⚪ `.venv/` - Virtual environment (2+ GB, can recreate with `uv sync`)
- ⚪ `__pycache__/` - Python cache (auto-generated)
- ⚪ `logs/` - Log files (unless you want to keep them)

### Never backup (security):
- ❌ `.env` files with API keys (if you create any)
- ❌ `credentials.json` (if you add Google Drive API)

---

## Restore from Backup

If you need to restore VALCORE1 from Google Drive:

### Method 1: Using Google Drive Desktop

1. **Install Google Drive Desktop** (if not already)
2. **Sign in**
3. **Navigate to VALCORE1 folder**
4. **Right-click folder**
5. **Select "Make available offline"**
6. **Files will download to:** `G:\My Drive\VALCORE1\`
7. **Copy to:** `C:\VALCORE1\`
8. **Reinstall dependencies:**
   ```powershell
   cd C:\VALCORE1
   uv sync --extra client
   ```

### Method 2: Web Download

1. **Go to:** https://drive.google.com
2. **Find your VALCORE1_Backup folder**
3. **Right-click → Download**
4. **Extract to:** `C:\VALCORE1\`
5. **Reinstall dependencies:**
   ```powershell
   cd C:\VALCORE1
   uv sync --extra client
   ```

---

## Storage Space

**VALCORE1 sizes:**
- With `.venv`: ~3.5 GB
- Without `.venv`: ~500 MB
- Just config files: ~50 KB
- Just code: ~5 MB

**Google Drive free tier:** 15 GB
- Enough for 4+ full backups
- Or 30+ code-only backups

**Tip:** Exclude `.venv` to save space

---

## Backup Schedule Recommendation

### Daily (Automatic):
- Configuration files only
- Quick (under 1 minute)

### Weekly (Manual):
- Full code backup
- Medium (5-10 minutes)

### Monthly (Manual):
- Complete system backup
- Full (30+ minutes first time)

### Before Changes:
- Always backup before:
  - Installing updates
  - Modifying code
  - Changing configs
  - Major system changes

---

## Troubleshooting

### "Not enough storage"

**Solution:**
1. Exclude `.venv` folder
2. Delete old backups
3. Upgrade to Google One (100 GB for $1.99/month)

### "Sync is slow"

**Solution:**
1. Sync during off-peak hours (night)
2. Exclude large files temporarily
3. Check internet speed

### "Files not syncing"

**Solution:**
1. Check Google Drive icon in system tray
2. Click "Resume syncing" if paused
3. Sign out and sign back in
4. Restart Google Drive app

### "Can't find my backup"

**Solution:**
1. Go to: https://drive.google.com
2. Search for: "VALCORE1"
3. Check "My Drive" vs "My Computer" sections
4. Check trash folder

---

## Security Tips

1. **Enable 2-Factor Authentication:**
   - Go to: https://myaccount.google.com/security
   - Turn on 2-Step Verification

2. **Don't share your Google account**

3. **Don't backup sensitive files:**
   - API keys
   - Passwords
   - Personal information

4. **Use strong password** for Google account

5. **Review who has access:**
   - Go to: https://drive.google.com
   - Right-click folder → "Share"
   - Make sure only you have access

---

## Alternative Backup Options

If you don't want to use Google Drive:

1. **OneDrive** (if you have Microsoft account)
2. **Dropbox** (2 GB free)
3. **External USB drive** (manual but offline)
4. **GitHub** (for code only, not large files)
5. **Local NAS** (if you have one)

---

## Summary

**Recommended setup:**
1. Use Google Drive Desktop app
2. Sync entire VALCORE1 folder
3. Exclude `.venv` to save space
4. Enable automatic sync
5. Verify backup weekly

**This gives you:**
- ✅ Automatic cloud backup
- ✅ Access from anywhere
- ✅ Version history
- ✅ Peace of mind

---

**Questions?** Check the `COMPLETE_SETUP_GUIDE.md` for more help!

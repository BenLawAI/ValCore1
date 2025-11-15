# VALCORE1 Quick Setup Checklist

**Print this page and check off each step as you complete it!**

---

## ☐ Part 1: Download (5 minutes)

### Windows Desktop:

1. ☐ Go to: https://github.com/BenLawAI/ValCore1
2. ☐ Click green "Code" button → "Download ZIP"
3. ☐ Extract ZIP to `C:\VALCORE1\`

---

## ☐ Part 2: Install on Windows (20 minutes)

### Install UV:

4. ☐ Open PowerShell as Administrator
5. ☐ Run: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
6. ☐ Verify: `uv --version`

### Run Setup:

7. ☐ Run: `cd C:\VALCORE1`
8. ☐ Run: `.\setup_with_uv.ps1`
9. ☐ Wait for "✅ UV setup complete!"

### Get API Key:

10. ☐ Sign up: https://console.picovoice.ai/signup
11. ☐ Copy your Access Key
12. ☐ Edit: `VALCORE1\01_Client_Brain\config\voice_config.json`
13. ☐ Replace `YOUR_ACCESS_KEY_HERE` with your key
14. ☐ Save file

---

## ☐ Part 3: Install on ATOM (20 minutes)

### Transfer Files:

15. ☐ Run: `scp -r C:\VALCORE1 ben@192.168.1.121:~/`
    - (Replace IP with your ATOM's IP)

### Install on ATOM:

16. ☐ SSH into ATOM: `ssh ben@192.168.1.121`
17. ☐ Run: `cd ~/ValCore1`
18. ☐ Run: `curl -LsSf https://astral.sh/uv/install.sh | sh`
19. ☐ Run: `export PATH="$HOME/.local/bin:$PATH"`
20. ☐ Run: `./setup_with_uv.sh`
21. ☐ Wait for completion

### Install Ollama:

22. ☐ Run: `curl -fsSL https://ollama.com/install.sh | sh`
23. ☐ Run: `ollama serve &`
24. ☐ Run: `ollama pull qwen2.5:14b`
25. ☐ Test: `ollama run qwen2.5:14b "Hello"`

---

## ☐ Part 4: Backup to Google Drive (30 minutes)

### Using Google Drive Desktop:

26. ☐ Download: https://www.google.com/drive/download/
27. ☐ Install and sign in
28. ☐ Add folder: `C:\VALCORE1\`
29. ☐ Choose "Sync with Google Drive"
30. ☐ Wait for initial sync

---

## ☐ Part 5: First Test (10 minutes)

### Start Server:

31. ☐ SSH to ATOM: `ssh ben@192.168.1.121`
32. ☐ Run: `cd ~/ValCore1`
33. ☐ Run: `uv run python VALCORE1/02_Server_Brain/main_server.py`
34. ☐ Look for: "✓ Server listening on 0.0.0.0:5000"

### Start Client:

35. ☐ On Windows: `cd C:\VALCORE1`
36. ☐ Run: `uv run python VALCORE1\01_Client_Brain\main_client.py`
37. ☐ Look for: "Listening for 'Hey Val'..."

### Test:

38. ☐ Say: "Hey Val"
39. ☐ Wait for beep
40. ☐ Say: "What time is it?"
41. ☐ Hear Val respond!

---

## ✅ You're Done!

**Total Time:** ~1.5 hours

**Next Steps:**
- ☐ Read: `COMPLETE_SETUP_GUIDE.md` for details
- ☐ Read: `UV_GUIDE.md` for UV commands
- ☐ Run: `VALCORE1\05_Setup_Scripts\Testing\RUN_ALL_TESTS.ps1`
- ☐ Enroll voice: `VALCORE1\05_Setup_Scripts\Voice_Enrollment\`

---

## Emergency Contacts

**Documentation:**
- Complete Guide: `COMPLETE_SETUP_GUIDE.md`
- UV Guide: `UV_GUIDE.md`
- Troubleshooting: `VALCORE1\04_Documentation\TROUBLESHOOTING_GUIDE.md`

**Quick Commands:**

```powershell
# Start Windows Client:
cd C:\VALCORE1
uv run python VALCORE1\01_Client_Brain\main_client.py

# Start ATOM Server:
ssh ben@192.168.1.121
uv run python VALCORE1/02_Server_Brain/main_server.py

# Run Tests:
.\VALCORE1\05_Setup_Scripts\Testing\RUN_ALL_TESTS.ps1

# Emergency Stop:
Ctrl+C  (or press Ctrl+Shift+Alt+V)
```

---

**Print this page and keep it handy!**

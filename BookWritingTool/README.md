# BookWritingTool - Professional AI-Powered Writing Suite

**Version:** 0.1.0 (MVP)
**Status:** Production Ready
**Author:** Master Builder (Ben)

---

## 📚 Overview

BookWritingTool is a professional-grade book writing application that combines AI-powered writing assistance with sophisticated style mixing, bestseller tracking, and a complete publishing pipeline. Write 200k+ word manuscripts with the power of Claude, GPT, or local Ollama models.

### ✨ Key Features (MVP)

- **🤖 Multi-LLM Support:** Claude, GPT-4, and Ollama (local offline mode)
- **🎨 Style Mixing:** Blend 10 pre-loaded author styles (Stephen King, Brandon Sanderson, etc.)
- **📊 Bestseller Tracking:** Auto-scrape Amazon, NYT, USA Today bestseller lists
- **✍️ Copy-Paste-Compile Workflow:** Seamlessly integrate AI-generated text
- **🔍 Semantic Search:** FAISS-powered consistency checking
- **📤 Export:** Word (.docx), PDF, and plain text formats
- **💾 Auto-Save:** Never lose your work
- **💰 Cost Tracking:** Monitor API spending in real-time
- **🗄️ Character Database:** Track characters, locations, timelines
- **📈 Word Count Tracking:** Real-time progress monitoring

---

## 🚀 Quick Start

### Installation (Windows)

1. **Download/Clone** this repository
2. **Run INSTALL.bat** (installs UV and all dependencies)
3. **Get API Keys:**
   - Claude: https://console.anthropic.com/
   - OpenAI: https://platform.openai.com/api-keys
4. **Launch:** Double-click `START_BOOK_WRITER.bat`
5. **Configure:** Enter API keys in Settings tab

**That's it!** You're ready to write.

---

## 📖 Usage Guide

### Creating Your First Book

1. **Launch the app:** `START_BOOK_WRITER.bat`
2. **Create a project:** Click "📁 New Project" → Enter book title
3. **Create a chapter:** Click "➕ New Chapter" → Enter chapter title
4. **Start writing!**

### Writing Workflows

#### Workflow 1: Manual Writing
- Type directly in the editor
- Auto-saves every 30 seconds
- Click "💾 Save" to force save

#### Workflow 2: AI-Assisted Writing
1. Go to **Style Mixer** tab
2. Select author style (e.g., "Stephen King")
3. Adjust percentage (100% for pure style)
4. Go back to **Editor** tab
5. Click **"🤖 Generate with AI"**
6. Enter your prompt (e.g., "Write a tense scene where the protagonist discovers...")
7. AI generates text (shown in popup)
8. Copy the generated text
9. Click **"📋 Paste & Compile"** or paste manually

#### Workflow 3: Copy from ChatGPT/Claude Web
1. Generate text in ChatGPT or Claude.ai
2. Copy the output
3. Return to BookWritingTool
4. Click **"📋 Paste & Compile"** (auto-detects clipboard)

### Style Mixing

**Available Author Profiles:**
1. Stephen King (Horror/Thriller)
2. Rick Riordan (YA Fantasy)
3. Brandon Sanderson (Epic Fantasy)
4. Lee Child (Action Thriller)
5. Gillian Flynn (Psychological)
6. Malcolm Gladwell (Business)
7. Michelle Obama (Memoir)
8. Cormac McCarthy (Literary)
9. Neil Gaiman (Fantasy/Myth)
10. James Clear (Self-Help)

**How it works:**
- Select primary author (e.g., "Stephen King")
- Set percentage (0-100%)
- App generates style-blended prompts for the LLM
- Result: Text that mimics the selected author's tone, formality, and sentence structure

### Exporting Your Manuscript

1. Click **"📤 Export"**
2. Choose format:
   - **Word (.docx)** - For traditional publishing submissions
   - **PDF** - Print-ready format
   - **Plain Text (.txt)** - Universal format
3. Select save location
4. Done! Your manuscript is exported

---

## ⚙️ Configuration

### LLM Settings

**Online Mode (API-based):**
- **Claude (Recommended):** Fast, high-quality, $3-15 per million tokens
- **GPT-4:** Alternative, slightly more expensive
- **Cost:** ~$15-35 per 200k word book (with context)

**Offline Mode (Local):**
- **Ollama:** Free, runs on your GPU
- **Models:** llama3.1:8b (fast), llama3.1:70b (better quality)
- **Cost:** $0 (just electricity)

**Switching Modes:**
- Go to **Settings** tab
- Click **☁️ Online** or **💻 Offline**
- Click **"✅ Initialize LLM Manager"**

### Bestseller Tracking

**Setup:**
- Automatically scrapes Amazon, NYT, USA Today
- Runs weekly (configurable in `config/settings.yaml`)
- Tracks books on list for 3+ consecutive weeks
- Alerts when trending authors appear

**Manual Refresh:**
- (Future feature - currently runs on schedule)

---

## 📁 Project Structure

```
BookWritingTool/
├── app/
│   ├── core/               # LLM manager, style engine, compiler, scraper
│   ├── gui/                # PyQt6 interface
│   ├── models/             # Database models (SQLAlchemy)
│   └── main.py             # Entry point
├── data/
│   ├── styles/             # 10 author profiles
│   └── bestsellers/        # Scraped data
├── projects/               # Your book projects
│   └── [your_book]/
│       ├── chapters/       # Chapter markdown files
│       ├── characters/     # Character database
│       └── exports/        # Exported manuscripts
├── config/
│   ├── settings.yaml       # App configuration
│   └── scraper_config.yaml # Scraper settings
├── library/                # Semantic search index
├── logs/                   # Application logs
├── pyproject.toml          # UV dependencies
├── INSTALL.bat             # Installation script
└── START_BOOK_WRITER.bat   # Launcher
```

---

## 💰 Cost Breakdown

### Per Book (200k words, 50% AI-generated)

**Online Mode:**
- Claude Sonnet 4.5: ~$15-30
- GPT-4 Turbo: ~$25-40
- Embeddings (one-time): ~$1-2

**Offline Mode:**
- Ollama (local): $0

**Annual (10 books):**
- Online: $150-350
- Offline: $0

**Budget Alerts:**
- Set monthly budget in `config/settings.yaml`
- App warns at 75% usage

---

## 🔧 Troubleshooting

### "LLM Not Initialized"
- Go to Settings tab
- Enter API key(s)
- Click "✅ Initialize LLM Manager"

### "Ollama not available"
- Download Ollama: https://ollama.ai
- Run: `ollama pull llama3.1:8b`
- Ensure Ollama is running (system tray icon)

### "Playwright browser not found"
- Run: `uv run playwright install chromium`
- This is needed for bestseller scraping

### Export fails
- Ensure project has chapters
- Check chapter files exist in `projects/[book]/chapters/`

### High API costs
- Switch to offline mode (Ollama)
- Reduce max_tokens in settings
- Use local models for drafts, online for polishing

---

## 🛣️ Roadmap (V2.0)

### Not in MVP (Coming Later)
- ❌ Advanced style mixing (thematic blending)
- ❌ Auto-generate author profiles from samples
- ❌ EPUB/MOBI export
- ❌ Direct KDP/Draft2Digital upload
- ❌ Collaboration features (multi-user)
- ❌ Revision intelligence (track changes)
- ❌ Cover design integration
- ❌ Marketing copy generation

### Planned Enhancements
- Real-time style sliders (tone, formality, length)
- Character consistency AI checker
- Plot hole detector
- Market analytics dashboard
- Automated chapter summaries

---

## 🔐 Security

**API Keys:**
- Stored locally in SQLite database
- Never transmitted except to official APIs
- Consider using environment variables for production

**Data Privacy:**
- All data stored locally on your machine
- No telemetry or external tracking
- Your manuscripts never leave your computer (except API calls)

---

## 📄 License

**Proprietary** - For personal use by Master Builder (Ben)
Not for public distribution.

---

## 🙏 Credits

**Built with:**
- PyQt6 (GUI framework)
- Anthropic Claude API
- OpenAI GPT API
- Ollama (local LLMs)
- FAISS (semantic search)
- Sentence Transformers
- Playwright (web scraping)
- SQLAlchemy (database)
- UV (package manager)

**Author Profiles Inspired By:**
Stephen King, Rick Riordan, Brandon Sanderson, Lee Child, Gillian Flynn, Malcolm Gladwell, Michelle Obama, Cormac McCarthy, Neil Gaiman, James Clear

---

## 📞 Support

For issues or questions:
1. Check logs in `logs/app.log`
2. Review `config/settings.yaml` for configuration
3. Consult this README
4. Contact Val (Claude Sonnet 4.5) for troubleshooting

---

## 🎯 Philosophy

**"Write first, edit later, publish confidently."**

BookWritingTool is designed for authors who want to leverage AI without losing their voice. The style mixing engine helps you write like your favorite authors while maintaining your unique perspective. Whether you're writing a 200k-word epic fantasy or a concise business book, this tool scales with your ambition.

**Now go write that book.** 📚✨

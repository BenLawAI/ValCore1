# VALCORE1 Library - Persistent Memory Storage

This directory contains all persistent memory and conversation data for VALCORE1.

## Directory Structure

### daily/
Stores daily conversation logs organized by room context.
- Automatic creation when conversations occur
- Files named by date: `YYYY-MM-DD.json`
- Contains full conversation history with timestamps

### monthly/
Contains compressed monthly summaries.
- Created by the memory compression system
- Aggregates daily logs into monthly summaries
- Preserves important context while reducing size

### yearly/
Long-term yearly archives.
- Created from monthly summaries
- Keeps only the most important information
- Enables long-term memory across years

### backups/
Pre-compression backups of all data.
- Automatic backups before compression runs
- Organized by room and timestamp
- Allows recovery if compression goes wrong

### rooms/
Room-specific persistent context.
- Stores room-specific settings and memory
- Updated as you switch between rooms
- Maintains continuity within each context

## Room Contexts

Each subdirectory contains data for one of four rooms:

- **general/** - General purpose assistant
- **truck/** - 2003 Dodge Ram 1500 2WD / Hellcat swap project
- **invoice/** - Contractor invoice generation
- **legal/** - Legal document assistance

## Data Format

All files use JSON format with this structure:
```json
{
  "date": "2025-11-14",
  "room": "general",
  "conversations": [
    {
      "timestamp": "2025-11-14T10:30:00",
      "user": "Hey Val, what time is it?",
      "assistant": "It's 10:30 AM, Boss.",
      "metadata": {
        "response_time_ms": 1250,
        "llm_used": "qwen2.5:14b",
        "server": "ATOM"
      }
    }
  ]
}
```

## Automatic Management

The memory compression system automatically:
- Creates daily logs as conversations occur
- Compresses daily logs into monthly summaries (monthly schedule)
- Compresses monthly logs into yearly archives (yearly schedule)
- Creates backups before any compression
- Removes old compressed data based on retention policy

See `VALCORE1/02_Server_Brain/config/compression_strategy.json` for configuration.

## Manual Access

You can manually explore these files to:
- Review past conversations
- Export conversation data
- Debug memory issues
- Analyze usage patterns

## Size Management

Expected sizes:
- Daily logs: 1-10 MB per day
- Monthly summaries: 10-50 MB per month
- Yearly archives: 50-200 MB per year

The compression system keeps storage manageable while preserving important context.

---

**Created by:** VALCORE1 Setup
**Date:** 2025-11-14

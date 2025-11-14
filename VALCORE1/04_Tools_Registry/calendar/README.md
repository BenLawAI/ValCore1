# Google Calendar MCP Server

Google Calendar integration for schedule management with VALCORE1.

## Purpose

Allows VALCORE1 to view, create, and manage calendar events through voice commands.

## Setup

### 1. Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Create new project: "VALCORE1 Calendar"
3. Enable Google Calendar API:
   - APIs & Services → Library
   - Search "Google Calendar API"
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
[System.Environment]::SetEnvironmentVariable('GCAL_CLIENT_ID', $creds.installed.client_id, 'User')
[System.Environment]::SetEnvironmentVariable('GCAL_CLIENT_SECRET', $creds.installed.client_secret, 'User')
```

### 4. Configure Time Zone

Edit `config.json`:
```json
{
  "enabled": true,
  "settings": {
    "calendar_options": {
      "time_zone": "America/New_York"  // Change to your timezone
    }
  }
}
```

### 5. First Run - OAuth Flow

When you first use Calendar commands:
1. VALCORE1 will open browser
2. Sign in to your Google account
3. Grant Calendar permissions
4. Token saved to `~/.valcore1/tokens/calendar_token.json`
5. Future use is automatic!

## Voice Commands

### Viewing Schedule

```
"Hey Val, what's on my schedule today?"
"Hey Val, show my calendar for tomorrow"
"Hey Val, when is my next meeting?"
"Hey Val, list my events for this week"
"Hey Val, do I have anything at 3pm?"
```

### Creating Events

```
"Hey Val, schedule a meeting tomorrow at 2pm"
Val: "What's the title?"
You: "Project review"
Val: "How long?"
You: "1 hour"
Val: "Create it? Yes or no"
You: "Yes"
```

### Managing Events

```
"Hey Val, cancel my 3pm meeting"
"Hey Val, reschedule tomorrow's meeting to 4pm"
"Hey Val, add John to the project meeting"
"Hey Val, set a reminder for my appointment"
```

### Quick Queries

```
"Hey Val, when am I free today?"
"Hey Val, do I have time for a 30 minute call?"
"Hey Val, what's my schedule like next week?"
```

## Configuration Options

### Default Event Settings

```json
{
  "calendar_options": {
    "default_duration_minutes": 60,
    "default_reminder_minutes": 15
  }
}
```

### Time Range

```json
{
  "event_options": {
    "look_ahead_days": 30,  // Show events up to 30 days ahead
    "look_back_days": 7     // Show past events from 7 days ago
  }
}
```

### Event Creation

```json
{
  "create_options": {
    "confirm_before_create": true,  // Always ask before creating
    "send_notifications": true,      // Notify attendees
    "add_description": true          // Add VALCORE1 note
  }
}
```

### Safety Settings

```json
{
  "safety": {
    "require_confirmation_for": [
      "delete",
      "modify_recurring",
      "invite_multiple"
    ],
    "max_attendees": 20
  }
}
```

## Scopes Explained

```
calendar.readonly  - View calendar only
calendar.events    - Create/modify events
calendar           - Full access (not recommended)
```

**Recommendation:** Use `readonly` + `events` for balance.

## Security Best Practices

1. **Confirm before creating**
   - `confirm_before_create: true`
   - Prevents accidental events

2. **Limit attendees**
   - `max_attendees: 20`
   - Prevents mass invites

3. **Require confirmation for deletes**
   - Prevents accidental data loss
   - Especially for recurring events

4. **Token security**
   - Token stored in `~/.valcore1/tokens/`
   - Never commit to git
   - Revoke at: https://myaccount.google.com/permissions

## Time Zone Handling

### Set Your Time Zone

Find your time zone: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

Common values:
- `America/New_York` - Eastern Time
- `America/Chicago` - Central Time
- `America/Denver` - Mountain Time
- `America/Los_Angeles` - Pacific Time
- `Europe/London` - UK
- `Asia/Tokyo` - Japan

## Natural Language Processing

VALCORE1 understands natural time expressions:

```
"tomorrow at 2pm"
"next Monday at 9am"
"in 30 minutes"
"3pm this Friday"
"two weeks from today"
"end of the month"
```

## Troubleshooting

### "OAuth error: invalid_client"
- Client ID/secret not set correctly

**Fix:** Verify environment variables:
```powershell
[System.Environment]::GetEnvironmentVariable('GCAL_CLIENT_ID', 'User')
```

### "Token expired"
- OAuth token needs refresh

**Fix:** Delete token and re-authenticate:
```powershell
Remove-Item $env:USERPROFILE\.valcore1\tokens\calendar_token.json
```

### "Event creation failed"
- Time conflict
- Invalid time format
- Calendar not accessible

**Fix:** Check event details, verify calendar access

### "Wrong time zone"
- Events appearing at wrong time

**Fix:** Update time_zone in config.json

## Advanced Configuration

### Multiple Calendars

Support multiple calendars:
```json
{
  "calendars": [
    {
      "name": "Work",
      "id": "work@example.com",
      "color": "blue"
    },
    {
      "name": "Personal",
      "id": "primary",
      "color": "green"
    }
  ]
}
```

Voice command:
```
"Hey Val, add this to my Work calendar"
```

### Smart Scheduling

Find available time slots:
```json
{
  "smart_scheduling": {
    "enabled": true,
    "working_hours": {
      "start": "09:00",
      "end": "17:00"
    },
    "buffer_minutes": 15
  }
}
```

### Recurring Events

Default recurring patterns:
```json
{
  "recurring_defaults": {
    "weekly_meetings": "FREQ=WEEKLY;COUNT=52",
    "monthly_reviews": "FREQ=MONTHLY;COUNT=12"
  }
}
```

## Privacy Considerations

### What Google Sees
- Your calendar events
- API usage logs
- OAuth grant history

### What VALCORE1 Stores
- OAuth token (encrypted)
- Event metadata cache
- Operation logs

### What's Sent to LLM
- Event details for processing
- Never sent to external servers
- Processed locally or on ATOM only

## Logs

Location: `04_Tools_Registry/logs/mcp_calendar.log`

Review logs to see:
- Calendar operations
- Event creation/modification
- API errors
- OAuth refresh events

---

**Status:** ⚪ Requires Setup (OAuth)
**Priority:** 5 (Optional)
**API Keys:** OAuth credentials required
**Free Tier:** Yes (unlimited calendar access)

# Web Search MCP Server

Internet search capabilities for VALCORE1.

## Purpose

Allows VALCORE1 to search the internet and retrieve information through voice commands.

## Setup

### Option 1: DuckDuckGo (Recommended - No API Key)

**No setup required!** DuckDuckGo works out of the box.

1. Edit `config.json`:
```json
{
  "enabled": true,
  "settings": {
    "provider": "duckduckgo"
  }
}
```

2. Done! Web search is ready.

### Option 2: Google Custom Search (Better Results - Requires API Key)

1. Get Google API credentials:
   - Go to: https://console.cloud.google.com/
   - Create project → Enable Custom Search API
   - Create credentials → API Key
   - Create Custom Search Engine: https://cse.google.com/

2. Set environment variables:
```powershell
# In PowerShell (one-time setup)
[System.Environment]::SetEnvironmentVariable('GOOGLE_SEARCH_API_KEY', 'your-api-key', 'User')
[System.Environment]::SetEnvironmentVariable('GOOGLE_SEARCH_CX', 'your-cx-id', 'User')
```

3. Enable in `config.json`:
```json
{
  "enabled": true,
  "settings": {
    "provider": "google",
    "providers": {
      "google": {
        "enabled": true
      }
    }
  }
}
```

### Option 3: Bing Search (Alternative - Requires API Key)

1. Get Bing Search API key:
   - Go to: https://azure.microsoft.com/en-us/services/cognitive-services/bing-web-search-api/
   - Sign up for free tier (3,000 searches/month)

2. Set environment variable:
```powershell
[System.Environment]::SetEnvironmentVariable('BING_SEARCH_API_KEY', 'your-api-key', 'User')
```

3. Enable in `config.json`:
```json
{
  "settings": {
    "provider": "bing",
    "providers": {
      "bing": {
        "enabled": true
      }
    }
  }
}
```

## Voice Commands

### Basic Search

```
"Hey Val, search for Python tutorials"
"Hey Val, look up the weather in Seattle"
"Hey Val, find information about electric cars"
```

### Research

```
"Hey Val, research Hellcat engine specs"
"Hey Val, find legal information about contracts"
"Hey Val, look up 2003 Dodge Ram maintenance schedule"
```

### Quick Facts

```
"Hey Val, what is the capital of France?"
"Hey Val, how tall is Mount Everest?"
"Hey Val, when was the Internet invented?"
```

## Configuration Options

### Max Results
```json
{
  "search_options": {
    "max_results": 10
  }
}
```

### Safe Search
```json
{
  "search_options": {
    "safe_search": true
  }
}
```

### Content Extraction
Extract full page content for detailed analysis:
```json
{
  "content_extraction": {
    "enabled": true,
    "max_page_size_kb": 500
  }
}
```

### Rate Limiting
Prevent quota exhaustion:
```json
{
  "rate_limit": {
    "enabled": true,
    "requests_per_minute": 20
  }
}
```

## Provider Comparison

| Provider | Cost | Setup | Quality | Rate Limit |
|----------|------|-------|---------|------------|
| DuckDuckGo | Free | None | Good | Unlimited |
| Google | Free tier | API key + CX | Excellent | 100/day free |
| Bing | Free tier | API key | Very Good | 3,000/month free |

**Recommendation:** Start with DuckDuckGo, upgrade to Google if you need better results.

## Privacy Considerations

### DuckDuckGo
- ✅ No tracking
- ✅ Anonymous searches
- ✅ Privacy-focused

### Google
- ⚠️ May track searches
- ⚠️ Requires account
- ✅ Can use project API key (not personal)

### Bing
- ⚠️ May track searches
- ⚠️ Microsoft account
- ✅ Can use subscription key

## Troubleshooting

### "Search quota exceeded"
- **DuckDuckGo:** Shouldn't happen (no quota)
- **Google:** Exceeded 100 searches/day
- **Bing:** Exceeded 3,000 searches/month

**Fix:** Wait for quota reset or upgrade plan

### "API key invalid"
- Environment variable not set correctly
- API key expired or revoked

**Fix:** Verify environment variables:
```powershell
[System.Environment]::GetEnvironmentVariable('GOOGLE_SEARCH_API_KEY', 'User')
```

### "No results found"
- Query too specific
- Safe search blocking results

**Fix:** Try broader query or disable safe search

## Logs

Location: `04_Tools_Registry/logs/mcp_web_search.log`

Review logs to see:
- Search queries made
- Results returned
- API errors
- Rate limit status

## Advanced Usage

### Caching
Results are cached for 1 hour by default:
```json
{
  "cache": {
    "enabled": true,
    "ttl_seconds": 3600
  }
}
```

Benefits:
- Faster repeated searches
- Reduced API usage
- Lower costs

### Custom User Agent
```json
{
  "search_options": {
    "user_agent": "VALCORE1/1.0"
  }
}
```

---

**Status:** 🟡 Ready (DuckDuckGo) / ⚪ Requires Setup (Google/Bing)
**Priority:** 5 (Useful)
**API Keys:** Optional (DuckDuckGo free, Google/Bing require keys)

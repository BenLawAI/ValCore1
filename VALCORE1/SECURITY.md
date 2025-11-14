# VALCORE1 Security Guide

## Overview

This document outlines the security features and best practices for deploying VALCORE1 in production environments.

## Security Features Implemented

### 1. HTTPS/TLS Support ✅

**Status:** Implemented

VALCORE1 supports HTTPS/TLS encryption for all API communications.

**Configuration:**

```bash
# Enable HTTPS in .env file
VALCORE1_HTTPS=true
```

**Self-Signed Certificates:**
- Automatically generated on first run if not provided
- Valid for 1 year
- Stored in `certs/` directory (gitignored)

**Production Certificates:**
```bash
# Use CA-signed certificates
SSL_CERT_PATH=/path/to/cert.crt
SSL_KEY_PATH=/path/to/private.key
```

**Generate self-signed cert manually:**
```bash
openssl req -x509 -newkey rsa:2048 -keyout valcore1.key -out valcore1.crt -days 365 -nodes
```

### 2. API Authentication ✅

**Status:** Implemented (Optional)

Protect your API with authentication keys.

**Setup:**

```bash
# Generate secure API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
VALCORE1_API_KEY=your_generated_key_here
```

**Usage:**
```bash
# Include in requests
curl -H "X-API-Key: your_api_key" https://server:5000/api/process
```

### 3. Rate Limiting ✅

**Status:** Implemented

Prevents abuse and DoS attacks with configurable rate limiting.

**Configuration:**

```bash
# .env file
RATE_LIMIT_REQUESTS=60      # Max requests
RATE_LIMIT_WINDOW=60        # Time window (seconds)
```

**Default:** 60 requests per minute per IP address

**Response when exceeded:**
```json
{
  "error": "Rate limit exceeded. Please try again later.",
  "status": "rate_limit_exceeded"
}
```

### 4. Input Validation & Sanitization ✅

**Status:** Implemented

All user inputs are validated and sanitized to prevent injection attacks.

**Protections:**
- SQL injection prevention
- XSS prevention
- Command injection prevention
- JSON validation with Pydantic
- Maximum input length limits
- Character filtering

**Validation Rules:**
- Session IDs: alphanumeric + underscore/hyphen, 1-64 chars
- Room names: alphanumeric + underscore, 1-32 chars
- User input: max 10,000 characters
- Control characters removed (except newlines/tabs)

### 5. CORS Configuration ✅

**Status:** Implemented

Cross-Origin Resource Sharing with configurable origins.

**Development:**
```bash
ALLOWED_ORIGINS=*
```

**Production:**
```bash
# Comma-separated list
ALLOWED_ORIGINS=https://app.example.com,https://dashboard.example.com
```

### 6. Custom Exception Handling ✅

**Status:** Implemented

Specific exception types for better error handling and security.

**Benefits:**
- Prevents information leakage
- Granular error handling
- Better logging and monitoring
- Appropriate HTTP status codes

**Example:**
```python
try:
    # Process request
except InputValidationError as e:
    # Return 400 Bad Request
except AuthenticationError as e:
    # Return 401 Unauthorized
except RateLimitError as e:
    # Return 429 Too Many Requests
```

### 7. Secure Logging ✅

**Status:** Implemented

Logs are configured to avoid sensitive data exposure.

**What's logged:**
- Request timestamps
- Session IDs
- Room names
- Error types
- Performance metrics

**What's NOT logged:**
- User input content (can be enabled with flag)
- API keys
- Passwords
- Raw conversation data

### 8. Environment Variables ✅

**Status:** Implemented

Sensitive configuration stored in environment variables, not code.

**Protected data:**
- API keys
- Database credentials
- SSL certificate paths
- Server hostnames

## Security Best Practices

### For Production Deployment

1. **Always use HTTPS**
   ```bash
   VALCORE1_HTTPS=true
   ```

2. **Enable API authentication**
   ```bash
   VALCORE1_API_KEY=<strong_random_key>
   ```

3. **Restrict CORS origins**
   ```bash
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

4. **Use CA-signed certificates**
   - Don't use self-signed certs in production
   - Let's Encrypt is free and automated

5. **Configure rate limiting**
   ```bash
   RATE_LIMIT_REQUESTS=30  # Lower for production
   RATE_LIMIT_WINDOW=60
   ```

6. **Secure the .env file**
   ```bash
   chmod 600 .env
   ```

7. **Regular updates**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

8. **Firewall configuration**
   ```bash
   # Only allow necessary ports
   ufw allow 5000/tcp  # VALCORE1 API
   ufw allow 11434/tcp # Ollama (localhost only recommended)
   ```

9. **Use reverse proxy**
   - Nginx or Apache in front of Flask
   - Better SSL/TLS termination
   - Additional security headers
   - Load balancing

10. **Monitor logs**
    ```bash
    tail -f logs/valcore1_server.log
    ```

### Network Security

**Tailscale VPN (Recommended):**

VALCORE1 is designed to work with Tailscale for secure remote access.

```bash
# On ATOM server
sudo tailscale up

# On desktop
tailscale ip -4 atom-server
```

**Benefits:**
- End-to-end encryption
- No port forwarding needed
- Zero-trust network
- Easy setup

**Firewall Rules:**

```bash
# ATOM server
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 100.0.0.0/8  # Tailscale network
sudo ufw enable
```

### Data Security

**Sensitive Data:**

VALCORE1 stores:
- Voice embeddings (for speaker verification)
- Conversation history (in FAISS index)
- Room contexts

**Protection:**
- All data stored locally
- No cloud dependencies
- FAISS index gitignored
- Voice profiles gitignored
- Backup encrypted (future enhancement)

**Data Retention:**

Configure in compression_schedule.json:
```json
{
  "daily": {
    "retention_days": 7
  },
  "monthly": {
    "retention_months": 12
  }
}
```

## Security Checklist

### Before Deployment

- [ ] HTTPS enabled
- [ ] API key configured (if needed)
- [ ] CORS origins restricted
- [ ] Rate limiting configured
- [ ] Firewall rules set
- [ ] .env file secured (chmod 600)
- [ ] Self-signed certs replaced with CA-signed
- [ ] Logs directory created
- [ ] Tailscale configured
- [ ] Backup strategy in place

### Regular Maintenance

- [ ] Review logs weekly
- [ ] Update dependencies monthly
- [ ] Rotate API keys quarterly
- [ ] Review access logs
- [ ] Test backup restoration
- [ ] Monitor resource usage
- [ ] Check SSL certificate expiry

## Vulnerability Reporting

**Security issues should be reported privately.**

Contact: [Your contact method]

Do not create public GitHub issues for security vulnerabilities.

## Testing Security

### Test HTTPS

```bash
curl https://localhost:5000/api/health
```

### Test Rate Limiting

```bash
for i in {1..70}; do
  curl -X POST https://localhost:5000/api/process \
    -H "Content-Type: application/json" \
    -d '{"user_input": "test"}'
done
```

### Test API Authentication

```bash
# Without key (should fail)
curl -X POST https://localhost:5000/api/process

# With key (should succeed)
curl -X POST https://localhost:5000/api/process \
  -H "X-API-Key: your_key"
```

### Run Unit Tests

```bash
cd /home/user/ValCore1/VALCORE1
pytest tests/ -v
```

## Known Limitations

1. **In-memory rate limiter**
   - Resets on server restart
   - Not shared across multiple instances
   - Consider Redis for production

2. **Self-signed certificates**
   - Browser warnings
   - Not suitable for public deployment
   - Use Let's Encrypt for production

3. **No database encryption at rest**
   - FAISS index stored unencrypted
   - Future enhancement planned

4. **Session management**
   - Simple session IDs
   - No expiration
   - Consider JWT tokens for production

## Future Security Enhancements

Planned for future releases:

- [ ] Data encryption at rest (AES-256)
- [ ] JWT token authentication
- [ ] Redis-backed rate limiting
- [ ] Audit logging
- [ ] Two-factor authentication (optional)
- [ ] IP whitelisting
- [ ] Automated security scanning
- [ ] Intrusion detection

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [Tailscale Documentation](https://tailscale.com/kb/)
- [Let's Encrypt](https://letsencrypt.org/)

---

**Last Updated:** 2025-11-14
**Security Review:** Required before production deployment

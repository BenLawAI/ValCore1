# VALCORE1 Dependency Management

## Version Pinning Strategy

All dependencies in VALCORE1 use **exact version pinning** (`==`) instead of version ranges (`>=`, `~=`). This ensures:

- **Reproducibility**: Every installation produces identical results
- **Security**: No automatic updates that could introduce vulnerabilities
- **Stability**: Prevents breaking changes from being automatically installed
- **Debugging**: Easier to diagnose issues when everyone uses the same versions

## Requirements Files

### Main Requirements
- `VALCORE1/requirements.txt` - Complete requirements for both client and server
- Use this for development or full system installation

### Component Requirements
- `VALCORE1/01_Client_Brain/setup/requirements_client.txt` - Client-only dependencies
- `VALCORE1/02_Server_Brain/setup/requirements_server.txt` - Server-only dependencies

## Updating Dependencies

### When to Update

Update dependencies when:
1. **Security vulnerabilities** are announced (high priority)
2. **Bug fixes** are available for issues you're experiencing
3. **New features** are needed from newer versions
4. **Regular maintenance** (quarterly review recommended)

### How to Update Safely

#### 1. Check for Updates

```bash
# Install pip-audit for security scanning
pip install pip-audit

# Check for security vulnerabilities
pip-audit

# List outdated packages
pip list --outdated
```

#### 2. Review Changelog

Before updating, review the changelog for:
- Breaking changes
- New requirements
- Deprecation warnings
- Bug fixes
- Security patches

Example:
```bash
# Visit package homepage or GitHub releases
# For example: https://github.com/pytorch/pytorch/releases
```

#### 3. Update One Package at a Time

```bash
# Update single package in isolated environment
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# or: test_env\Scripts\activate  # Windows

pip install package-name==NEW_VERSION
```

#### 4. Test Thoroughly

```bash
# Run full test suite
pytest

# Test specific components
pytest tests/server/test_backup_manager.py
pytest tests/client/test_automation.py

# Run integration tests
pytest -m integration

# Manual testing of critical features
# - Voice recognition
# - API endpoints
# - Backup system
# - LLM responses
```

#### 5. Update Requirements File

```bash
# After testing, update the version in requirements.txt
# Change: package-name==OLD_VERSION
# To:     package-name==NEW_VERSION

# Update the "Last updated" date in the file header
```

#### 6. Commit Changes

```bash
git add requirements.txt
git commit -m "Update package-name from OLD to NEW

Changelog:
- Feature: Description
- Fix: Description
- Security: Description

Testing:
- All unit tests pass
- Integration tests pass
- Manual testing completed"
```

## Security Updates

### Critical Security Updates

When a security vulnerability is announced:

1. **Assess Impact**: Determine if vulnerability affects VALCORE1
2. **Update Immediately**: Don't wait for regular maintenance cycle
3. **Test Quickly**: Run automated tests and smoke test critical features
4. **Deploy**: Update production systems ASAP

### Security Scanning

```bash
# Weekly security scan (recommended)
pip-audit

# Check for known vulnerabilities
pip install safety
safety check

# GitHub Security Alerts
# Enable Dependabot in GitHub repository settings
```

## Dependency Conflicts

### Resolving Conflicts

If packages have conflicting requirements:

1. **Check dependency tree**:
   ```bash
   pip install pipdeptree
   pipdeptree --packages package-name
   ```

2. **Find compatible versions**:
   ```bash
   # Use pip's dependency resolver
   pip install package-a==X.Y.Z package-b==A.B.C
   ```

3. **Create virtual environment for testing**:
   ```bash
   python -m venv conflict_test
   # Test different version combinations
   ```

### Common Conflicts

- **PyTorch + CUDA**: Ensure PyTorch version matches CUDA toolkit
- **transformers + sentence-transformers**: Keep versions aligned
- **Flask + Werkzeug**: Flask requires specific Werkzeug versions

## Version Ranges (Not Used in VALCORE1)

We **do not use** version ranges for security and stability:

- `>=1.0.0` - ANY version >= 1.0.0 (dangerous, could install 999.0.0)
- `~=1.2.0` - Compatible release (1.2.0 to <1.3.0) (still allows patches)
- `==1.2.3` - EXACT version (what we use) ✓

## Platform-Specific Dependencies

### Windows-Specific
```python
pywin32==308; sys_platform == 'win32'
```

### GPU-Specific
```bash
# CUDA 12.1
torch==2.1.2+cu121 -f https://download.pytorch.org/whl/torch_stable.html

# CPU-only
torch==2.1.2
```

## Dependency Groups

### Core Dependencies (Always Required)
- torch, numpy, scipy - Core computation
- flask, requests - Web framework and HTTP
- pydantic, python-dotenv - Configuration

### Voice System (Client Only)
- faster-whisper, pyaudio - Speech recognition
- pvporcupine - Wake word detection
- resemblyzer - Speaker verification

### LLM System (Server Only)
- ollama - LLM interface
- sentence-transformers, faiss-cpu - Semantic search
- transformers - NLP models

### Testing (Development Only)
- pytest, pytest-cov - Testing framework
- pytest-mock, pytest-timeout - Testing utilities

## Best Practices

### 1. Lock File
Consider using `pip freeze` to generate lock file:

```bash
# Generate lock file with exact versions
pip freeze > requirements.lock

# Install from lock file
pip install -r requirements.lock
```

### 2. Separate Dev Dependencies
Keep development dependencies separate:

```txt
# requirements.txt - production
flask==3.0.3
numpy==1.26.4

# requirements-dev.txt - development only
pytest==8.3.4
black==24.10.0
ipython==8.31.0
```

### 3. Document Why Versions Are Pinned

Add comments for non-obvious version constraints:

```txt
# Pinned to 2.1.2 due to CUDA 12.1 compatibility
torch==2.1.2

# Pinned to 3.0.3 for security fix CVE-2024-XXXXX
flask==3.0.3
```

### 4. Regular Audits
- Monthly: `pip list --outdated`
- Weekly: `pip-audit` for security
- Quarterly: Review and update all dependencies

## Dependency Update Schedule

| Frequency | Task |
|-----------|------|
| Weekly | Security vulnerability scan |
| Monthly | Check for outdated packages |
| Quarterly | Review and test updates |
| As Needed | Critical security patches |
| Annually | Major version upgrades |

## Breaking Changes

When updating packages with breaking changes:

1. **Read Migration Guide**: Most packages provide migration docs
2. **Update Code**: Adapt to new APIs
3. **Update Tests**: Fix broken tests
4. **Update Documentation**: Reflect API changes
5. **Communicate**: Inform team of breaking changes

## Rollback Strategy

If update causes issues:

1. **Revert commit**: `git revert <commit-hash>`
2. **Reinstall old versions**: `pip install -r requirements.txt`
3. **Test rollback**: Ensure system works
4. **Investigate issue**: Debug before retry

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [pip Documentation](https://pip.pypa.io/)
- [pip-audit Documentation](https://pypi.org/project/pip-audit/)
- [Safety Documentation](https://pyup.io/safety/)

## Support

For dependency issues:
1. Check package documentation
2. Search GitHub issues
3. Review VALCORE1 test suite
4. Contact maintainers if needed

---

Last updated: 2025-01-14

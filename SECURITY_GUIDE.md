# 🔒 SECURITY AND SENSITIVE DATA GUIDE

## ⚠️ CRITICAL SECURITY ALERT

This repository contains **SENSITIVE DATA** that must be handled carefully before pushing to GitHub or any public repository.

## 🚨 IMMEDIATE ACTIONS REQUIRED

### 1. Files with Hardcoded API Keys (MUST FIX BEFORE PUSHING)

The following files contain **hardcoded API keys** that need to be removed:

- `backend/smart_verification.py` - Line 22: NewsAPI key
- `backend/simple_verification.py` - Line 16: NewsAPI key
- `backend/bedrock_integration.py` - Line 23: AWS Bedrock API key

### 2. Environment Variables File (.env)

The `.env` file contains real API keys and credentials:

```
GNEWS_API_KEY=cbbfce891c792d42676aaf1b01fe06f3
CURRENTS_API_KEY=e5kXI-_B355CtMY6LPxcyOy8E_sGHEuX0KiewSIxVK0m80eC
NEWSAPI_KEY=ebe74bd45e474f518aa0e4e826a9c086
AWS_ACCESS_KEY_ID=BedrockAPIKey-4a4q-at-385240721237
AWS_SECRET_ACCESS_KEY=ABSKQmVkcm9ja0FQSUtleS00YTRxLWF0LTM4NTI0MDcyMTIzNzo3Y0VQRERLM2JlZnI0d1lrQ1FwdVMxUHV4Q1FEVkcwcjI4Sm8yQzBMQVE1V2R1OWYvRjRlK0dVM3lyUT0=
```

## ✅ SECURITY CHECKLIST BEFORE PUSHING TO GITHUB

### Step 1: Fix Hardcoded API Keys

- [ ] Replace hardcoded API keys in Python files with `os.getenv()`
- [ ] Ensure all files use environment variables from `.env`

### Step 2: Verify .gitignore Coverage

- [ ] `.env` file is listed in `.gitignore` ✅
- [ ] `instance/` directory (contains SQLite database) is ignored ✅
- [ ] `__pycache__/` directories are ignored ✅

### Step 3: Environment Setup

- [ ] Create `.env.example` file with dummy values
- [ ] Document environment variable requirements in README

### Step 4: Database Security

- [ ] Ensure `instance/trustify.db` is not committed (contains user data)
- [ ] Verify database credentials are in environment variables

## 🔧 HOW TO FIX HARDCODED API KEYS

### Replace this pattern:

```python
self.newsapi_key = "ebe74bd45e474f518aa0e4e826a9c086"  # ❌ NEVER DO THIS
```

### With this pattern:

```python
import os
from dotenv import load_dotenv

load_dotenv()
self.newsapi_key = os.getenv('NEWSAPI_KEY')  # ✅ SECURE
```

## 📝 RECOMMENDED WORKFLOW

1. **Before First Push:**

   ```bash
   # Check what files would be committed
   git status

   # Ensure .env is not listed (should be ignored)
   # If .env appears, add it to .gitignore
   ```

2. **For Collaborators:**
   - Copy `.env.example` to `.env`
   - Add their own API keys to `.env`
   - Never commit the `.env` file

## 🌍 ENVIRONMENT VARIABLES NEEDED

Create these environment variables in your `.env` file:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# News API Keys
GNEWS_API_KEY=your-gnews-api-key
CURRENTS_API_KEY=your-currents-api-key
NEWSAPI_KEY=your-newsapi-key
THENEWSAPI_KEY=your-thenewsapi-key
GUARDIAN_API_KEY=your-guardian-api-key
WOLRDNEWS_API_KEY=your-worldnews-api-key

# AI Service API Keys
COHERE_API_KEY=your-cohere-api-key
OPENROUTER_API_KEY=your-openrouter-api-key
GEMINI_API_KEY=your-gemini-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=us-east-1
```

## 🔄 ROTATING COMPROMISED KEYS

If any API keys have been exposed:

1. **Immediately revoke/regenerate** all exposed keys
2. Update the keys in your `.env` file
3. **Never commit the old keys** to version control

## 📚 ADDITIONAL SECURITY BEST PRACTICES

- Use strong, unique passwords for all services
- Enable 2FA where available
- Regularly rotate API keys
- Monitor API usage for unusual activity
- Use least-privilege access for AWS IAM users
- Consider using AWS Secrets Manager for production

## 🚀 DEPLOYMENT CONSIDERATIONS

For production deployment:

- Use cloud provider secret management (AWS Secrets Manager, Azure Key Vault, etc.)
- Set environment variables in your deployment platform
- Never store secrets in container images
- Use HTTPS for all external API calls

---

**Remember: Security is everyone's responsibility! 🔐**

# 🚀 Quick Start - User Token Management

## ✅ What's New

Your bot now supports **user-provided API tokens** with an interactive setup workflow!

## 🎯 Workflow

```
START → Select AI Provider → Check Token → Request Token (if needed) → Select Model → CHAT!
```

## 📁 New Files

1. **`app/user_tokens.py`** - User token storage manager
2. **`app/handlers.py`** - Complete rewrite with FSM workflow
3. **`app/ai_services.py`** - Updated to accept user tokens

## 🎮 How to Test

### 1. Start the Bot
```bash
# Make sure you have the dependencies
docker-compose up -d

# Or with Python
pip install -r app/requirements.txt
cd app
python main.py
```

### 2. Test the Workflow in Telegram

#### New User (No Tokens Configured):
```
You: /start
Bot: 👋 Welcome! Let's setup your AI provider
     [🚀 Setup AI Provider button]

You: [Click Setup]
Bot: Select AI Provider:
     ➕ Setup CHATGPT
     ➕ Setup GEMINI
     ➕ Setup CLAUDE

You: [Select CHATGPT]
Bot: 🔑 API Token Required
     Get it from: https://platform.openai.com/api-keys
     Send your API key now:

You: sk-proj-yourkey123...
Bot: ✅ Token saved securely!
     [Message auto-deleted for security]
     
Bot: 🎯 Select Model:
     - gpt-4o
     - gpt-4o-mini
     - gpt-4-turbo

You: [Select gpt-4o-mini]
Bot: ✅ Setup Complete!
     Provider: CHATGPT
     Model: gpt-4o-mini
     Now send a message to start chatting!

You: Hello, how are you?
Bot: [AI Response]
     — ChatGPT (gpt-4o-mini)
```

#### Returning User (Has Tokens):
```
You: /start
Bot: Select AI Provider:
     ✅ (Your Token) CHATGPT
     ✅ (Your Token) GEMINI
     ➕ Setup CLAUDE

You: [Selects GEMINI]
Bot: [Model selection...]
User: [Selects model]
Bot: ✅ Setup complete!
[Chat continues with Gemini]
```

#### With Admin Token (Env Var):
```
# If admin has OPENAI_API_KEY in .env:

You: /start
Bot: Select AI Provider:
     ✅ (Global) CHATGPT  ← Admin configured
     ➕ Setup GEMINI

You: [Select CHATGPT]
[Uses admin's token, no need for user token]
```

## 📝 New Commands

### `/start`
Interactive setup workflow - select provider, provide token if needed, choose model

### `/myconfig`
```
You: /myconfig
Bot: ⚙️ Your Configuration
     Provider: CHATGPT
     Tokens configured: 2
     Messages: 8
```

### `/settoken`
Add or update a token for any provider
```
You: /settoken
Bot: [Shows provider list]
You: [Selects GEMINI]
Bot: [Requests token]
You: [Provides token]
Bot: ✅ Token updated!
```

### `/removetoken`
Remove a stored token
```
You: /removetoken
Bot: 🗑️ Remove Token
     - Remove CHATGPT
     - Remove GEMINI
You: [Selects one]
Bot: ✅ Token removed
```

### `/cleardata`
Remove ALL user data (tokens + history)
```
You: /cleardata
Bot: ⚠️ Clear all data?
     [Yes] [No]
You: [Yes]
Bot: ✅ All data cleared!
```

### `/clear`
Clear only conversation history (keeps tokens)

## 🔒 Security Features

### 1. Auto-Delete Token Messages
When user sends API key, the message is automatically deleted

### 2. Memory-Only Storage
Tokens stored in RAM, not on disk (lost on restart)

### 3. User Isolation
Each user's tokens are completely separate

### 4. Easy Removal
`/removetoken` or `/cleardata` commands

## 📊 Testing Scenarios

### Scenario 1: New User, No Admin Tokens
- User must provide their own token
- Bot guides through entire setup
- Token saved, model selected, ready to chat

### Scenario 2: Admin Tokens Available
- User can use admin tokens (Global)
- Or provide their own (Your Token)
- Choice between providers

### Scenario 3: Multiple Providers
- User sets up multiple tokens
- Can switch between providers with `/start`
- Each maintains separate model preference

### Scenario 4: Token Management
- `/myconfig` - View current setup
- `/settoken` - Add new provider
- `/removetoken` - Remove one
- `/cleardata` - Clear everything

## ⚠️ Important Notes

### Current Implementation (Memory):
- ✅ Works immediately
- ✅ Simple testing
- ❌ Tokens lost on restart
- ❌ No encryption

### For Production (Use Redis):
```python
# Replace user_tokens.py storage with:
import redis
from cryptography.fernet import Fernet

redis_client = redis.Redis(host='localhost', port=6379)
cipher = Fernet(ENCRYPTION_KEY)
```

## 🧪 Complete Test Checklist

- [ ] `/start` as completely new user
- [ ] Provide API token (check auto-delete)
- [ ] Select model
- [ ] Send message and get AI response
- [ ] `/myconfig` shows correct info
- [ ] `/start` again (should show "Your Token")
- [ ] `/settoken` add second provider
- [ ] Switch between providers
- [ ] `/removetoken` for one provider
- [ ] `/cleardata` removes everything
- [ ] Test with admin token (env var)
- [ ] Test token priority (user > env)

## 🎉 Summary

Your bot now has:
- ✅ Interactive setup workflow
- ✅ User-specific token management
- ✅ Privacy-focused design
- ✅ FSM-based state handling
- ✅ Secure token entry
- ✅ Easy provider switching
- ✅ Complete token management commands

**Workflow:** Start → Provider → Token (if needed) → Model → Chat!

---

For detailed technical documentation, see:
- `USER_TOKEN_GUIDE.md` - Complete implementation details
- `README.md` - General bot documentation
- `SETUP.md` - Quick setup guide

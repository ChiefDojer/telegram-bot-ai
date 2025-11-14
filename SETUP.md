# Quick Setup Guide

## 🚀 Get Started in 3 Steps

### Step 1: Get Your Bot Token
1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Copy the bot token you receive

### Step 2: Get AI API Keys (Choose at least one)

#### Option A: ChatGPT (OpenAI)
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

#### Option B: Google Gemini
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API key"
4. Copy the key

#### Option C: Claude (Anthropic)
1. Go to https://console.anthropic.com/
2. Sign up for an account
3. Navigate to API Keys
4. Create and copy a new key (starts with `sk-ant-`)

#### Option D: Grok (xAI)
1. Go to https://console.x.ai/
2. Sign up for beta access
3. Create API key
4. Copy the key (starts with `xai-`)

#### Option E: Custom LLM (Local/Self-hosted)
Use Ollama, LM Studio, or any OpenAI-compatible API:
```bash
# Example: Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
# URL: http://localhost:11434/v1/chat/completions
```

### Step 3: Configure and Run

#### Using Docker (Easiest)
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env and add your tokens
notepad .env  # Windows
nano .env     # Linux/Mac

# 3. Start the bot
docker-compose up -d

# 4. Check logs
docker-compose logs -f
```

#### Using Python
```bash
# 1. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 2. Install dependencies
pip install -r app/requirements.txt

# 3. Copy and edit environment
cp .env.example .env
notepad .env  # Edit with your tokens

# 4. Run the bot
cd app
python main.py
```

## 🎉 That's It!

Open Telegram and:
1. Find your bot by username
2. Send `/start`
3. Use `/ai` to select AI provider
4. Start chatting!

## ⚙️ Minimum .env Configuration

```env
# Required
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# Add at least ONE of these:
OPENAI_API_KEY=sk-proj-xxxxx...
# OR
GEMINI_API_KEY=AIzaSyXXXX...
# OR
ANTHROPIC_API_KEY=sk-ant-xxxxx...
# OR
XAI_API_KEY=xai-xxxxx...
# OR
CUSTOM_LLM_BASE_URL=http://localhost:11434/v1/chat/completions
```

## 🆘 Need Help?

**Bot not responding?**
- Verify bot token is correct
- Make sure at least one AI service is configured
- Check logs: `docker-compose logs -f` or check terminal output

**Import errors?**
- Install dependencies: `pip install -r app/requirements.txt`
- Use Docker for hassle-free setup

**AI not working?**
- Check API key is valid and not expired
- Verify you have credits/quota remaining
- Test with different AI provider

## 📊 Cost Estimates

| Provider | Cost | Free Tier |
|----------|------|-----------|
| ChatGPT | ~$0.002 per 1K tokens | $5 free credit (new users) |
| Gemini | Free tier | 60 requests/min free |
| Claude | ~$0.003 per 1K tokens | No free tier |
| Grok | TBD | Beta access |
| Custom (Ollama) | FREE | Unlimited (self-hosted) |

## 🎯 Next Steps

After setup:
- Read the full [README.md](README.md) for detailed documentation
- Try different AI providers with `/ai`
- Check status with `/status`
- Clear history with `/clear` to start fresh conversations

---

Need more help? Check the full README or open an issue on GitHub!

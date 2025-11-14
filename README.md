# 🤖 Telegram Bot AI

Multi-AI provider Telegram bot built with Aiogram v3. Chat with ChatGPT, Google Gemini, Claude, Grok, or your own custom LLM!

## ✨ Features

- 🔄 **Multiple AI Providers**: Switch between different AI models on the fly
- 💬 **Conversation Context**: Maintains chat history for coherent conversations
- 🎯 **Easy Setup**: Simple configuration through environment variables
- 🐳 **Docker Ready**: Containerized deployment with Docker Compose
- 🔌 **Custom LLM Support**: Works with any OpenAI-compatible API (Ollama, LM Studio, etc.)

## 🧠 Supported AI Providers

| Provider | Models | API Key Required |
|----------|--------|------------------|
| **ChatGPT** (OpenAI) | gpt-4o-mini, gpt-4o, gpt-4-turbo | ✅ OPENAI_API_KEY |
| **Google Gemini** | gemini-1.5-flash, gemini-1.5-pro | ✅ GEMINI_API_KEY |
| **Claude** (Anthropic) | claude-3-5-sonnet, claude-3-opus | ✅ ANTHROPIC_API_KEY |
| **Grok** (xAI) | grok-beta, grok-vision-beta | ✅ XAI_API_KEY |
| **Custom LLM** | Any OpenAI-compatible API | ⚙️ CUSTOM_LLM_BASE_URL |

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+ or Docker
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- At least one AI service API key

### 2. Clone and Configure

```bash
# Clone the repository
git clone <your-repo-url>
cd telegram-bot-ai

# Copy environment template
cp .env.example .env

# Edit .env and add your credentials
notepad .env  # Windows
# or
nano .env     # Linux/Mac
```

### 3. Add Your API Keys

Edit `.env` and add your credentials:

```env
# Required
BOT_TOKEN=your_telegram_bot_token

# Add at least one AI service
OPENAI_API_KEY=sk-...          # For ChatGPT
GEMINI_API_KEY=...             # For Google Gemini
ANTHROPIC_API_KEY=sk-ant-...   # For Claude
XAI_API_KEY=xai-...            # For Grok

# Optional: Custom LLM (e.g., Ollama)
CUSTOM_LLM_BASE_URL=http://localhost:11434/v1/chat/completions
CUSTOM_LLM_MODEL=llama3
```

### 4. Run with Docker (Recommended)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### 5. Or Run with Python

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r app/requirements.txt

# Run the bot
cd app
python main.py
```

## 📱 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see welcome message |
| `/ai` | Select AI provider |
| `/help` | Show available commands |
| `/status` | Check current AI configuration |
| `/clear` | Clear conversation history |
| `/about` | About this bot |

## 💡 Usage Examples

### Basic Chat
1. Start the bot: `/start`
2. Select an AI: `/ai`
3. Send any message to chat!

### Switch AI Providers
```
You: /ai
Bot: [Shows available AI providers]
You: [Select ChatGPT]
You: Hello!
Bot: Hi! How can I help you today?
     — ChatGPT (gpt-4o-mini)
```

### Check Status
```
You: /status
Bot: 🤖 AI Bot Status
     Current AI: ChatGPT (gpt-4o-mini)
     Configured Services: 3/5
     ✅ ChatGPT (gpt-4o-mini)
     ✅ Google Gemini (gemini-1.5-flash)
     ❌ Claude (claude-3-5-sonnet)
     ❌ Grok (grok-beta)
     ✅ Custom LLM (llama3)
     Conversation messages: 4
```

## 🔧 Configuration

### AI Service Models

You can customize models by editing `app/ai_services.py`:

```python
# Change ChatGPT model
ChatGPTService(model="gpt-4o")  # Default: gpt-4o-mini

# Change Gemini model
GeminiService(model="gemini-1.5-pro")  # Default: gemini-1.5-flash

# Change Claude model
ClaudeService(model="claude-3-opus-20240229")  # Default: claude-3-5-sonnet
```

### Custom LLM Setup

#### Using Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3

# Configure in .env
CUSTOM_LLM_BASE_URL=http://localhost:11434/v1/chat/completions
CUSTOM_LLM_MODEL=llama3
```

#### Using LM Studio
```env
CUSTOM_LLM_BASE_URL=http://localhost:1234/v1/chat/completions
CUSTOM_LLM_MODEL=your-model-name
```

## 📁 Project Structure

```
telegram-bot-ai/
├── app/
│   ├── __init__.py
│   ├── main.py              # Bot entry point
│   ├── handlers.py          # Command and message handlers
│   ├── ai_services.py       # AI provider implementations
│   ├── requirements.txt     # Python dependencies
│   └── requirements-test.txt
├── docker-compose.yml       # Docker configuration
├── Dockerfile              # Container image definition
└── .env.example            # Environment template
```

## 🔒 Security Notes

- Never commit your `.env` file with real API keys
- Keep your bot token and API keys secure
- Use environment variables in production
- Regularly rotate API keys
- Monitor API usage and costs

## 🐛 Troubleshooting

### Bot not responding
- Check if bot token is correct
- Verify at least one AI service is configured
- Check logs: `docker-compose logs -f`

### AI service not available
- Verify API key is set correctly
- Check API key permissions and quotas
- Ensure no typos in environment variable names

### Custom LLM connection issues
- Verify the base URL is accessible
- Check if the endpoint is OpenAI-compatible
- Test the endpoint manually with curl

## 📊 API Rate Limits

| Provider | Free Tier | Notes |
|----------|-----------|-------|
| OpenAI | Limited credits | Pay as you go |
| Google Gemini | 60 requests/min | Free tier available |
| Anthropic | No free tier | Pay as you go |
| xAI Grok | Beta access | Check xAI console |
| Custom LLM | Depends on setup | Self-hosted = unlimited |

## 🛠️ Development

### Running Tests
```bash
cd app
pytest test_handlers.py
```

### Adding New AI Provider
1. Create new service class in `ai_services.py` extending `AIService`
2. Implement required methods: `generate_response()`, `is_available()`, `name`
3. Add to `AIServiceManager.services` dictionary
4. Update documentation

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review logs for error messages

## 🙏 Acknowledgments

- [Aiogram](https://github.com/aiogram/aiogram) - Telegram Bot framework
- [OpenAI](https://openai.com/) - ChatGPT API
- [Google](https://ai.google.dev/) - Gemini API
- [Anthropic](https://www.anthropic.com/) - Claude API
- [xAI](https://x.ai/) - Grok API

---

Built with ❤️ using Python and Aiogram v3

"""
Bot Handlers - Message and Command Processing
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

# Create router for handlers
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command"""
    await message.answer(
        f"👋 <b>Hello, {message.from_user.first_name}!</b>\n\n"
        "I'm a Telegram bot built with Aiogram v3.\n"
        "Send /help to see available commands."
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = (
        "<b>📚 Available Commands:</b>\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/about - About this bot\n"
        "/date - Show current date and time\n\n"
        "Just send me any message and I'll echo it back!"
    )
    await message.answer(help_text)


@router.message(Command("about"))
async def cmd_about(message: Message):
    """Handle /about command"""
    about_text = (
        "<b>🤖 About This Bot</b>\n\n"
        "Framework: Aiogram v3\n"
        "Language: Python 3.11+\n"
        "Hosting: Azure Container Instances\n\n"
        "Built with ❤️ using the telegram-bot-base template"
    )
    await message.answer(about_text)


@router.message(Command("date"))
async def cmd_date(message: Message):
    """Handle /date command"""
    from datetime import datetime
    import pytz
    
    # Default to UTC, but you can change this to your preferred timezone
    timezone = pytz.UTC
    current_date = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S %Z")
    await message.answer(f"📅 Current date and time: {current_date}")

@router.message(F.text)
async def echo_message(message: Message):
    """Echo any text message"""
    await message.answer(f"You said: {message.text}")


@router.message()
async def handle_other(message: Message):
    """Handle non-text messages"""
    await message.reply("I can only handle text messages for now. 📝")

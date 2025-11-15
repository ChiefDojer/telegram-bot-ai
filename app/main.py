"""
Telegram Bot - Main Entry Point
Built with Aiogram v3
"""
import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

# Import handlers
from handlers import router

# Load environment variables
load_dotenv()

# Get bot name from environment
BOT_NAME = os.getenv("BOT_NAME", "TelegramBot-AI")

# Configure logging with custom factory to add botname
class BotNameFilter(logging.Filter):
    def filter(self, record):
        record.botname = BOT_NAME
        return True

log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(botname)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Add the filter to root logger
logging.getLogger().addFilter(BotNameFilter())
logger = logging.getLogger(__name__)

async def main():
    """Initialize and start the bot"""
    # Get bot token from environment
    bot_token = os.getenv("BOT_TOKEN")
    
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables!")
        return
    
    # Initialize bot and dispatcher
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # Register handlers
    dp.include_router(router)
    
    # Set bot commands for the menu
    await bot.set_my_commands([
        BotCommand(command="start", description="🚀 Setup AI Provider"),
        BotCommand(command="help", description="📚 Show help & commands"),
        BotCommand(command="myconfig", description="⚙️ View your configuration"),
        BotCommand(command="settoken", description="🔑 Add/update API token"),
        BotCommand(command="removetoken", description="🗑️ Remove API token"),
        BotCommand(command="clear", description="🧹 Clear chat history"),
        BotCommand(command="cleardata", description="⚠️ Clear all data & tokens"),
        BotCommand(command="about", description="ℹ️ About this bot")
    ])
    
    # Start polling
    logger.info("Bot started successfully with FSM support!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

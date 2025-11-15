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
    
    # Start polling
    logger.info("Bot started successfully with FSM support!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

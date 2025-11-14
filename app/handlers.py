"""
Bot Handlers - Message and Command Processing with FSM
"""
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ai_services import AIServiceManager
from user_tokens import user_token_manager
import logging

router = Router()
ai_manager = AIServiceManager()
user_conversations = {}
logger = logging.getLogger(__name__)

class SetupStates(StatesGroup):
    selecting_provider = State()
    selecting_model = State()
    entering_token = State()

class TokenManagement(StatesGroup):
    selecting_provider_for_token = State()
    entering_new_token = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_providers = user_token_manager.get_user_providers(user_id)
    has_env_providers = len(ai_manager.get_available_services()) > 0
    
    if user_providers or has_env_providers:
        await show_provider_selection(message, state)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🚀 Setup AI Provider", callback_data="setup_start")]])
        await message.answer(
            f"👋 <b>Welcome, {message.from_user.first_name}!</b>\n\n"
            "I support: ChatGPT, Gemini, Claude, Grok, Custom LLM\n\n"
            "🔐 Your tokens stored only in bot memory\n"
            "Use /cleardata to remove them anytime",
            reply_markup=keyboard
        )

@router.callback_query(F.data == "setup_start")
async def setup_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await show_provider_selection(callback.message, state)

async def show_provider_selection(message: Message, state: FSMContext):
    user_id = message.from_user.id
    all_services = ai_manager.get_all_services()
    keyboard_buttons = []
    
    for service_id, service in all_services.items():
        has_env = service.is_available()
        has_user_token = user_token_manager.has_token(user_id, service_id)
        status = "✅ (Global)" if has_env else ("✅ (Your Token)" if has_user_token else "➕ Setup")
        keyboard_buttons.append([InlineKeyboardButton(text=f"{status} {service.name}", callback_data=f"select_provider_{service_id}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await state.set_state(SetupStates.selecting_provider)
    
    if isinstance(message, Message):
        await message.answer("🤖 Select AI Provider:", reply_markup=keyboard)
    else:
        await message.edit_text("🤖 Select AI Provider:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("select_provider_"), StateFilter(SetupStates.selecting_provider, None))
async def select_provider(callback: CallbackQuery, state: FSMContext):
    provider_id = callback.data.replace("select_provider_", "")
    user_id = callback.from_user.id
    await state.update_data(selected_provider=provider_id)
    
    service = ai_manager.get_service(provider_id)
    has_env = service.is_available()
    has_user_token = user_token_manager.has_token(user_id, provider_id)
    
    if has_env or has_user_token:
        await show_model_selection(callback, state, provider_id)
    else:
        await request_token(callback, state, provider_id)
    await callback.answer()

async def show_model_selection(callback: CallbackQuery, state: FSMContext, provider_id: str):
    models = ai_manager.get_models_for_provider(provider_id)
    keyboard_buttons = [[InlineKeyboardButton(text=model, callback_data=f"select_model_{model}")] for model in models]
    keyboard_buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_providers")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await state.set_state(SetupStates.selecting_model)
    await callback.message.edit_text(f"🎯 Select Model for {provider_id.upper()}:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("select_model_"), StateFilter(SetupStates.selecting_model))
async def select_model(callback: CallbackQuery, state: FSMContext):
    model = callback.data.replace("select_model_", "")
    data = await state.get_data()
    provider_id = data.get("selected_provider")
    user_id = callback.from_user.id
    
    user_token_manager.set_preferred_provider(user_id, provider_id)
    if user_token_manager.has_token(user_id, provider_id):
        user_token_manager.set_model(user_id, provider_id, model)
    
    await state.clear()
    await callback.answer("✅ Setup complete!")
    await callback.message.edit_text(f"✅ Setup Complete!\n\nProvider: {provider_id.upper()}\nModel: {model}\n\nSend a message to start chatting!")

async def request_token(callback: CallbackQuery, state: FSMContext, provider_id: str):
    instructions = {
        "chatgpt": "https://platform.openai.com/api-keys",
        "gemini": "https://makersuite.google.com/app/apikey",
        "claude": "https://console.anthropic.com/",
        "grok": "https://console.x.ai/",
        "custom": "Your custom LLM endpoint"
    }
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_token_entry")]])
    await state.set_state(SetupStates.entering_token)
    await callback.message.edit_text(
        f"🔑 API Token Required for {provider_id.upper()}\n\n"
        f"Get it from: {instructions.get(provider_id, 'API provider')}\n\n"
        "⚠️ Token stored only in memory\n"
        "Send your API key now:",
        reply_markup=keyboard
    )

@router.message(StateFilter(SetupStates.entering_token))
async def receive_token(message: Message, state: FSMContext):
    user_id = message.from_user.id
    token = message.text.strip()
    try:
        await message.delete()
    except:
        pass
    
    data = await state.get_data()
    provider_id = data.get("selected_provider")
    user_token_manager.set_token(user_id, provider_id, token)
    
    conf_msg = await message.answer(f"✅ Token saved for {provider_id.upper()}!\n\nNow select a model...")
    
    class MockCallback:
        def __init__(self, msg):
            self.message = msg
            self.from_user = msg.from_user
    
    await show_model_selection(MockCallback(conf_msg), state, provider_id)

@router.callback_query(F.data == "cancel_token_entry")
async def cancel_token_entry(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Cancelled. Use /start to try again.")
    await callback.answer()

@router.callback_query(F.data == "back_to_providers")
async def back_to_providers(callback: CallbackQuery, state: FSMContext):
    await show_provider_selection(callback.message, state)
    await callback.answer()

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>📚 Commands:</b>\n\n"
        "/start - Setup AI\n"
        "/settoken - Add token\n"
        "/removetoken - Remove token\n"
        "/myconfig - Show config\n"
        "/cleardata - Clear all data\n"
        "/clear - Clear chat history\n"
        "/about - About bot"
    )

@router.message(Command("myconfig"))
async def cmd_myconfig(message: Message):
    user_id = message.from_user.id
    config = user_token_manager.get_user_config(user_id)
    text = "<b>⚙️ Your Configuration</b>\n\n"
    text += f"Provider: {config.get('preferred_provider', 'None')}\n"
    text += f"Tokens configured: {len(config.get('configured_providers', []))}\n"
    text += f"Messages: {len(user_conversations.get(user_id, []))}"
    await message.answer(text)

@router.message(Command("cleardata"))
async def cmd_cleardata(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Yes", callback_data="confirm_cleardata"), InlineKeyboardButton(text="❌ No", callback_data="cancel_cleardata")]
    ])
    await message.answer("⚠️ Clear all data (tokens + history)?", reply_markup=keyboard)

@router.callback_query(F.data == "confirm_cleardata")
async def confirm_cleardata(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_token_manager.clear_user_data(user_id)
    if user_id in user_conversations:
        del user_conversations[user_id]
    await callback.message.edit_text("✅ All data cleared!")
    await callback.answer()

@router.callback_query(F.data == "cancel_cleardata")
async def cancel_cleardata(callback: CallbackQuery):
    await callback.message.edit_text("❌ Cancelled.")
    await callback.answer()

@router.message(Command("clear"))
async def cmd_clear(message: Message):
    user_id = message.from_user.id
    if user_id in user_conversations:
        del user_conversations[user_id]
    await message.answer("🗑️ History cleared!")

@router.message(Command("about"))
async def cmd_about(message: Message):
    await message.answer("🤖 AI Telegram Bot\n\nMulti-provider support\nBuilt with Aiogram v3")

@router.message(F.text)
async def handle_ai_message(message: Message):
    user_id = message.from_user.id
    provider_id = user_token_manager.get_preferred_provider(user_id)
    
    if not provider_id:
        await message.answer("❌ No AI selected! Use /start")
        return
    
    user_token = user_token_manager.get_token(user_id, provider_id)
    user_model = user_token_manager.get_model(user_id, provider_id)
    ai_service = ai_manager.get_service(provider_id, model=user_model, user_id=user_id)
    
    if not ai_service or not ai_service.is_available(user_token):
        await message.answer(f"❌ {provider_id.upper()} not configured! Use /settoken")
        return
    
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        response = await ai_service.generate_response(message.text, user_conversations[user_id], user_token)
        user_conversations[user_id].append({"role": "user", "content": message.text})
        user_conversations[user_id].append({"role": "assistant", "content": response})
        
        if len(user_conversations[user_id]) > 10:
            user_conversations[user_id] = user_conversations[user_id][-10:]
        
        await message.answer(f"{response}\n\n<i>— {ai_service.name}</i>")
    except Exception as e:
        logger.error(f"AI error: {e}")
        await message.answer(f"❌ Error: {str(e)}")

@router.message()
async def handle_other(message: Message):
    await message.reply("I can only handle text messages. 📝")

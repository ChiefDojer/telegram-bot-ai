"""
Unit Tests for Bot Handlers
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, User, Chat, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers import (
    cmd_start,
    cmd_help,
    cmd_about,
    cmd_myconfig,
    cmd_cleardata,
    cmd_clear,
    handle_ai_message,
    handle_other,
    setup_start,
    select_provider,
    select_model,
    receive_token,
    confirm_cleardata,
    cancel_cleardata,
    SetupStates
)


# Helper functions
def create_mock_message(text=None, from_user_id=12345, from_user_first_name="TestUser", chat_id=12345):
    """Create a mock Message object for testing"""
    message = MagicMock(spec=Message)
    message.text = text
    message.message_id = 1
    message.date = datetime.now()
    
    # Mock user
    user = MagicMock(spec=User)
    user.id = from_user_id
    user.first_name = from_user_first_name
    user.last_name = "LastName"
    user.username = "testuser"
    user.is_bot = False
    message.from_user = user
    
    # Mock chat
    chat = MagicMock(spec=Chat)
    chat.id = chat_id
    chat.type = "private"
    message.chat = chat
    
    # Mock bot
    message.bot = MagicMock()
    message.bot.send_chat_action = AsyncMock()
    
    # Mock answer, reply, and delete methods
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    message.delete = AsyncMock()
    
    return message


def create_mock_callback(data=None, from_user_id=12345, from_user_first_name="TestUser"):
    """Create a mock CallbackQuery object for testing"""
    callback = MagicMock(spec=CallbackQuery)
    callback.data = data
    callback.id = "callback_123"
    
    # Mock user
    user = MagicMock(spec=User)
    user.id = from_user_id
    user.first_name = from_user_first_name
    user.last_name = "LastName"
    user.username = "testuser"
    user.is_bot = False
    callback.from_user = user
    
    # Mock message
    callback.message = create_mock_message(from_user_id=from_user_id, from_user_first_name=from_user_first_name)
    callback.message.edit_text = AsyncMock()
    
    # Mock answer method
    callback.answer = AsyncMock()
    
    return callback


def create_mock_state():
    """Create a mock FSMContext for testing"""
    state = MagicMock(spec=FSMContext)
    state._data = {}
    
    async def mock_set_state(new_state):
        state._current_state = new_state
    
    async def mock_get_data():
        return state._data.copy()
    
    async def mock_update_data(**kwargs):
        state._data.update(kwargs)
    
    async def mock_clear():
        state._data = {}
        state._current_state = None
    
    state.set_state = AsyncMock(side_effect=mock_set_state)
    state.get_data = AsyncMock(side_effect=mock_get_data)
    state.update_data = AsyncMock(side_effect=mock_update_data)
    state.clear = AsyncMock(side_effect=mock_clear)
    
    return state


class TestStartCommand:
    """Tests for /start command handler"""
    
    @pytest.mark.asyncio
    @patch('handlers.user_token_manager')
    @patch('handlers.ai_manager')
    async def test_cmd_start_no_providers_shows_setup(self, mock_ai_manager, mock_token_manager):
        """Test that /start shows setup button when no providers configured"""
        message = create_mock_message(text="/start")
        state = create_mock_state()
        
        mock_token_manager.get_user_providers.return_value = []
        mock_ai_manager.get_available_services.return_value = []
        
        await cmd_start(message, state)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args
        assert "Welcome" in call_args[0][0]
        assert call_args[1]['reply_markup'] is not None
    
    @pytest.mark.asyncio
    @patch('handlers.user_token_manager')
    @patch('handlers.ai_manager')
    async def test_cmd_start_with_providers_shows_selection(self, mock_ai_manager, mock_token_manager):
        """Test that /start shows provider selection when providers available"""
        message = create_mock_message(text="/start")
        state = create_mock_state()
        
        mock_token_manager.get_user_providers.return_value = ["chatgpt"]
        
        await cmd_start(message, state)
        
        message.answer.assert_called_once()
        assert state.set_state.called


class TestHelpCommand:
    """Tests for /help command handler"""
    
    @pytest.mark.asyncio
    async def test_cmd_help_sends_help_text(self):
        """Test that /help command sends help information"""
        message = create_mock_message(text="/help")
        
        await cmd_help(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "Commands" in call_args
        assert "/start" in call_args
        assert "/myconfig" in call_args
        assert "/about" in call_args
    
    @pytest.mark.asyncio
    async def test_cmd_help_includes_new_commands(self):
        """Test that /help includes all new commands"""
        message = create_mock_message(text="/help")
        
        await cmd_help(message)
        
        call_args = message.answer.call_args[0][0]
        assert "/settoken" in call_args or "/myconfig" in call_args
        assert "/cleardata" in call_args


class TestAboutCommand:
    """Tests for /about command handler"""
    
    @pytest.mark.asyncio
    async def test_cmd_about_sends_about_text(self):
        """Test that /about command sends about information"""
        message = create_mock_message(text="/about")
        
        await cmd_about(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "Bot" in call_args or "AI" in call_args
        assert "Aiogram" in call_args


class TestMyConfigCommand:
    """Tests for /myconfig command handler"""
    
    @pytest.mark.asyncio
    @patch('handlers.user_token_manager')
    @patch('handlers.user_conversations', {})
    async def test_cmd_myconfig_shows_configuration(self, mock_token_manager):
        """Test that /myconfig shows user configuration"""
        message = create_mock_message(text="/myconfig")
        
        mock_token_manager.get_user_config.return_value = {
            'preferred_provider': 'chatgpt',
            'configured_providers': ['chatgpt', 'gemini']
        }
        
        await cmd_myconfig(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "Configuration" in call_args


class TestClearDataCommand:
    """Tests for /cleardata command handler"""
    
    @pytest.mark.asyncio
    async def test_cmd_cleardata_requests_confirmation(self):
        """Test that /cleardata requests user confirmation"""
        message = create_mock_message(text="/cleardata")
        
        await cmd_cleardata(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args
        assert "Clear" in call_args[0][0] or "clear" in call_args[0][0]
        assert call_args[1]['reply_markup'] is not None
    
    @pytest.mark.asyncio
    @patch('handlers.user_token_manager')
    @patch('handlers.user_conversations', {12345: []})
    async def test_confirm_cleardata_clears_all_data(self, mock_token_manager):
        """Test that confirming cleardata removes all user data"""
        callback = create_mock_callback(data="confirm_cleardata")
        
        await confirm_cleardata(callback)
        
        mock_token_manager.clear_user_data.assert_called_once_with(12345)
        callback.message.edit_text.assert_called_once()
        callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cancel_cleardata_cancels_operation(self):
        """Test that canceling cleardata stops the operation"""
        callback = create_mock_callback(data="cancel_cleardata")
        
        await cancel_cleardata(callback)
        
        callback.message.edit_text.assert_called_once()
        assert "Cancelled" in callback.message.edit_text.call_args[0][0]


class TestClearCommand:
    """Tests for /clear command handler"""
    
    @pytest.mark.asyncio
    @patch('handlers.user_conversations', {12345: [{"role": "user", "content": "test"}]})
    async def test_cmd_clear_clears_history(self):
        """Test that /clear removes conversation history"""
        message = create_mock_message(text="/clear")
        
        await cmd_clear(message)
        
        message.answer.assert_called_once()
        assert "cleared" in message.answer.call_args[0][0].lower()


class TestCallbackHandlers:
    """Tests for callback query handlers"""
    
    @pytest.mark.asyncio
    @patch('handlers.user_token_manager')
    @patch('handlers.ai_manager')
    async def test_setup_start_shows_providers(self, mock_ai_manager, mock_token_manager):
        """Test that setup_start callback shows provider selection"""
        callback = create_mock_callback(data="setup_start")
        state = create_mock_state()
        
        mock_token_manager.get_user_providers.return_value = []
        
        await setup_start(callback, state)
        
        callback.answer.assert_called_once()
        callback.message.answer.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('handlers.user_token_manager')
    @patch('handlers.ai_manager')
    async def test_select_provider_with_token_shows_models(self, mock_ai_manager, mock_token_manager):
        """Test that selecting a provider with token shows model selection"""
        callback = create_mock_callback(data="select_provider_chatgpt")
        state = create_mock_state()
        
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_ai_manager.get_service.return_value = mock_service
        mock_ai_manager.get_models_for_provider.return_value = ["gpt-4o", "gpt-4o-mini"]
        mock_token_manager.has_token.return_value = False
        
        await select_provider(callback, state)
        
        state.update_data.assert_called()
        callback.message.edit_text.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('handlers.user_token_manager')
    async def test_select_model_completes_setup(self, mock_token_manager):
        """Test that selecting a model completes setup"""
        callback = create_mock_callback(data="select_model_gpt-4o")
        state = create_mock_state()
        state._data = {"selected_provider": "chatgpt"}
        
        mock_token_manager.has_token.return_value = True
        
        await select_model(callback, state)
        
        state.clear.assert_called_once()
        callback.answer.assert_called_once()
        callback.message.edit_text.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('handlers.user_token_manager')
    @patch('handlers.ai_manager')
    async def test_receive_token_stores_token(self, mock_ai_manager, mock_token_manager):
        """Test that receiving a token stores it correctly"""
        message = create_mock_message(text="sk-test-token-12345")
        state = create_mock_state()
        state._data = {"selected_provider": "chatgpt"}
        
        mock_ai_manager.get_models_for_provider.return_value = ["gpt-4o", "gpt-4o-mini"]
        
        await receive_token(message, state)
        
        mock_token_manager.set_token.assert_called_once()
        message.delete.assert_called_once()


class TestAIMessageHandler:
    """Tests for AI message handler"""
    
    @pytest.mark.asyncio
    @patch('handlers.user_token_manager')
    async def test_handle_ai_message_no_provider_shows_error(self, mock_token_manager):
        """Test that messages without provider show error"""
        message = create_mock_message(text="Hello AI")
        
        mock_token_manager.get_preferred_provider.return_value = None
        
        await handle_ai_message(message)
        
        message.answer.assert_called_once()
        assert "No AI selected" in message.answer.call_args[0][0]
    
    @pytest.mark.asyncio
    @patch('handlers.user_token_manager')
    @patch('handlers.ai_manager')
    @patch('handlers.user_conversations', {})
    async def test_handle_ai_message_sends_to_ai(self, mock_ai_manager, mock_token_manager):
        """Test that messages are sent to AI service"""
        message = create_mock_message(text="Hello AI")
        
        mock_token_manager.get_preferred_provider.return_value = "chatgpt"
        mock_token_manager.get_token.return_value = "sk-test"
        mock_token_manager.get_model.return_value = "gpt-4o"
        
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_service.generate_response = AsyncMock(return_value="Hello! How can I help?")
        mock_service.name = "ChatGPT (gpt-4o)"
        mock_ai_manager.get_service.return_value = mock_service
        
        await handle_ai_message(message)
        
        mock_service.generate_response.assert_called_once()
        message.answer.assert_called_once()
        assert "Hello! How can I help?" in message.answer.call_args[0][0]
    
    @pytest.mark.asyncio
    @patch('handlers.user_token_manager')
    @patch('handlers.ai_manager')
    @patch('handlers.user_conversations', {})
    async def test_handle_ai_message_handles_errors(self, mock_ai_manager, mock_token_manager):
        """Test that AI errors are handled gracefully"""
        message = create_mock_message(text="Hello AI")
        
        mock_token_manager.get_preferred_provider.return_value = "chatgpt"
        mock_token_manager.get_token.return_value = "sk-test"
        mock_token_manager.get_model.return_value = "gpt-4o"
        
        mock_service = MagicMock()
        mock_service.is_available.return_value = True
        mock_service.generate_response = AsyncMock(side_effect=Exception("API Error"))
        mock_ai_manager.get_service.return_value = mock_service
        
        await handle_ai_message(message)
        
        message.answer.assert_called_once()
        assert "Error" in message.answer.call_args[0][0]


class TestHandleOther:
    """Tests for non-text message handler"""
    
    @pytest.mark.asyncio
    async def test_handle_other_replies_to_non_text(self):
        """Test that non-text messages get appropriate response"""
        message = create_mock_message()
        message.text = None  # Simulate non-text message (photo, sticker, etc.)
        
        await handle_other(message)
        
        message.reply.assert_called_once()
        call_args = message.reply.call_args[0][0]
        assert "text messages" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_handle_other_includes_emoji(self):
        """Test that response includes helpful emoji"""
        message = create_mock_message()
        message.text = None
        
        await handle_other(message)
        
        call_args = message.reply.call_args[0][0]
        assert "📝" in call_args


class TestIntegration:
    """Integration tests for handlers"""
    
    @pytest.mark.asyncio
    async def test_critical_handlers_are_async(self):
        """Test that all handlers are async functions"""
        import inspect
        handlers = [
            cmd_start, cmd_help, cmd_about, cmd_myconfig, 
            cmd_cleardata, cmd_clear, handle_ai_message, handle_other
        ]
        
        for handler in handlers:
            assert inspect.iscoroutinefunction(handler), f"{handler.__name__} should be async"
    
    @pytest.mark.asyncio
    async def test_command_handlers_accept_message_parameter(self):
        """Test that command handlers accept Message parameter"""
        import inspect
        handlers = [cmd_help, cmd_about, cmd_myconfig, cmd_cleardata, cmd_clear]
        
        for handler in handlers:
            sig = inspect.signature(handler)
            params = list(sig.parameters.keys())
            assert 'message' in params, f"{handler.__name__} should accept 'message' parameter"
    
    @pytest.mark.asyncio
    async def test_fsm_handlers_accept_state_parameter(self):
        """Test that FSM handlers accept state parameter"""
        import inspect
        sig = inspect.signature(cmd_start)
        params = list(sig.parameters.keys())
        assert 'state' in params, "cmd_start should accept 'state' parameter"


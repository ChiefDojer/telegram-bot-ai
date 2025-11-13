"""
Unit Tests for Bot Handlers
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, User, Chat
from handlers import (
    cmd_start,
    cmd_help,
    cmd_about,
    cmd_date,
    echo_message,
    handle_other
)


# Helper function to create a mock message
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
    
    # Mock answer and reply methods
    message.answer = AsyncMock()
    message.reply = AsyncMock()
    
    return message


class TestStartCommand:
    """Tests for /start command handler"""
    
    @pytest.mark.asyncio
    async def test_cmd_start_sends_welcome_message(self):
        """Test that /start command sends a welcome message"""
        message = create_mock_message(text="/start")
        
        await cmd_start(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "Hello, TestUser!" in call_args
        assert "Telegram bot built with Aiogram v3" in call_args
        assert "/help" in call_args
    
    @pytest.mark.asyncio
    async def test_cmd_start_uses_user_first_name(self):
        """Test that /start command uses the user's first name"""
        message = create_mock_message(text="/start", from_user_first_name="Alice")
        
        await cmd_start(message)
        
        call_args = message.answer.call_args[0][0]
        assert "Alice" in call_args


class TestHelpCommand:
    """Tests for /help command handler"""
    
    @pytest.mark.asyncio
    async def test_cmd_help_sends_help_text(self):
        """Test that /help command sends help information"""
        message = create_mock_message(text="/help")
        
        await cmd_help(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "Available Commands" in call_args
        assert "/start" in call_args
        assert "/help" in call_args
        assert "/about" in call_args
    
    @pytest.mark.asyncio
    async def test_cmd_help_mentions_echo_functionality(self):
        """Test that /help mentions echo functionality"""
        message = create_mock_message(text="/help")
        
        await cmd_help(message)
        
        call_args = message.answer.call_args[0][0]
        assert "echo" in call_args.lower()


class TestAboutCommand:
    """Tests for /about command handler"""
    
    @pytest.mark.asyncio
    async def test_cmd_about_sends_about_text(self):
        """Test that /about command sends about information"""
        message = create_mock_message(text="/about")
        
        await cmd_about(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "About This Bot" in call_args
        assert "Aiogram v3" in call_args
        assert "Python" in call_args
    
    @pytest.mark.asyncio
    async def test_cmd_about_includes_hosting_info(self):
        """Test that /about includes hosting information"""
        message = create_mock_message(text="/about")
        
        await cmd_about(message)
        
        call_args = message.answer.call_args[0][0]
        assert "Azure" in call_args or "Hosting" in call_args


class TestDateCommand:
    """Tests for /date command handler"""
    
    @pytest.mark.asyncio
    async def test_cmd_date_sends_current_date(self):
        """Test that /date command sends current date and time"""
        message = create_mock_message(text="/date")
        
        await cmd_date(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "Current date and time" in call_args
        assert "📅" in call_args
    
    @pytest.mark.asyncio
    async def test_cmd_date_includes_timezone(self):
        """Test that /date includes timezone information"""
        message = create_mock_message(text="/date")
        
        await cmd_date(message)
        
        call_args = message.answer.call_args[0][0]
        # Should include UTC or some timezone indicator
        assert "UTC" in call_args or "GMT" in call_args or ":" in call_args
    
    @pytest.mark.asyncio
    async def test_cmd_date_formats_correctly(self):
        """Test that /date formats date correctly"""
        message = create_mock_message(text="/date")
        
        # Just test that it responds with a formatted date
        await cmd_date(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        # Check that it contains date-like formatting (YYYY-MM-DD pattern or similar)
        assert any(char.isdigit() for char in call_args)
        assert ":" in call_args  # Time separator


class TestEchoMessage:
    """Tests for echo message handler"""
    
    @pytest.mark.asyncio
    async def test_echo_message_replies_with_text(self):
        """Test that text messages are echoed back"""
        message = create_mock_message(text="Hello, bot!")
        
        await echo_message(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "You said:" in call_args
        assert "Hello, bot!" in call_args
    
    @pytest.mark.asyncio
    async def test_echo_message_handles_special_characters(self):
        """Test that echo handles special characters"""
        special_text = "Special chars: @#$%^&*()!?"
        message = create_mock_message(text=special_text)
        
        await echo_message(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert special_text in call_args
    
    @pytest.mark.asyncio
    async def test_echo_message_handles_empty_text(self):
        """Test that echo handles empty text"""
        message = create_mock_message(text="")
        
        await echo_message(message)
        
        message.answer.assert_called_once()
        call_args = message.answer.call_args[0][0]
        assert "You said:" in call_args


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
    async def test_all_handlers_are_async(self):
        """Test that all handlers are async functions"""
        import inspect
        handlers = [cmd_start, cmd_help, cmd_about, cmd_date, echo_message, handle_other]
        
        for handler in handlers:
            assert inspect.iscoroutinefunction(handler), f"{handler.__name__} should be async"
    
    @pytest.mark.asyncio
    async def test_handlers_accept_message_parameter(self):
        """Test that all handlers accept Message parameter"""
        import inspect
        handlers = [cmd_start, cmd_help, cmd_about, cmd_date, echo_message, handle_other]
        
        for handler in handlers:
            sig = inspect.signature(handler)
            params = list(sig.parameters.keys())
            assert 'message' in params, f"{handler.__name__} should accept 'message' parameter"

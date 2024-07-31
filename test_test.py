import pytest
from unittest.mock import AsyncMock, MagicMock
from handlers.register import RegisterHandler
from handlers.notes import NotesHandler
from utils.notifications import NotificationService
from aiogram.types import Message


@pytest.mark.asyncio
async def test_start_command():
    message = MagicMock(spec=Message)
    state = AsyncMock()
    message.from_user = MagicMock(id=12345)
    db_mock = MagicMock()
    db_mock.fetchrow = AsyncMock(return_value=None)

    handler = RegisterHandler(db_mock)
    await handler.start_command(message, state)

    state.set_state.assert_called_once()
    message.answer.assert_called_once_with("Добро пожаловать! Пожалуйста, введите ваше имя:")


@pytest.mark.asyncio
async def test_process_email_invalid_email():
    message = MagicMock(spec=Message)
    state = AsyncMock()
    db_mock = MagicMock()
    handler = RegisterHandler(db_mock)

    message.text = "invalid_email"
    await handler.process_email(message, state)

    message.answer.assert_called_once_with("Некорректный email. Пожалуйста, введите правильный адрес "
                                           "электронной почты.")


@pytest.mark.asyncio
async def test_add_note_command():
    message = MagicMock(spec=Message)
    state = AsyncMock()
    db_mock = MagicMock()
    handler = NotesHandler(db_mock)

    await handler.add_note_command(message, state)
    message.answer.assert_called_once_with("Введите текст заметки:")


@pytest.mark.asyncio
async def test_process_note_time_invalid_format():
    message = MagicMock(spec=Message)
    state = AsyncMock()
    db_mock = MagicMock()
    handler = NotesHandler(db_mock)

    message.text = "тест дата"
    await handler.process_note_time(message, state)

    message.answer.assert_called_once_with("Неверный формат даты. Пожалуйста, используйте формат 'YYYY-MM-DD HH:MM'")


@pytest.mark.asyncio
async def test_check_reminders():
    bot = AsyncMock()
    db_mock = MagicMock()
    db_mock.fetch = AsyncMock(return_value=[
        {'telegram_id': 12345, 'text': 'Reminder text'}
    ])
    notification_service = NotificationService(db_mock, bot)
    await notification_service.check_reminders()
    bot.send_message.assert_called_once_with(12345, "Напоминание: Reminder text")

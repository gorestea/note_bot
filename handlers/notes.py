from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from datetime import datetime
from db import Database


class AddNoteState(StatesGroup):
    """
    Состояния для добавления заметки.
    """
    text = State()
    time = State()


class NotesHandler:
    """
    Обработчик команд и состояний, связанных с заметками.
    """

    def __init__(self, db: Database):
        self.db = db
        self.router = Router()

    def register(self, router: Router):
        """
        Регистрирует хендлеры для работы с заметками.
        """
        self.router.message.register(self.add_note_command, Command(commands=["addnote"]))
        self.router.message.register(self.process_note_text, AddNoteState.text)
        self.router.message.register(self.process_note_time, AddNoteState.time)
        self.router.message.register(self.list_notes, Command(commands=["mynotes"]))
        router.include_router(self.router)

    async def add_note_command(self, message: Message, state: FSMContext):
        """
        Обрабатывает команду /addnote, запрашивая текст заметки.
        """
        await message.answer("Введите текст заметки:")
        await state.set_state(AddNoteState.text)

    async def process_note_text(self, message: Message, state: FSMContext):
        """
        Обрабатывает введенный текст заметки и запрашивает время напоминания.
        """
        await state.update_data(text=message.text)
        await state.set_state(AddNoteState.time)
        await message.answer("Введите время напоминания в формате 'YYYY-MM-DD HH:MM':")

    async def process_note_time(self, message: Message, state: FSMContext):
        """
        Обрабатывает введенное время напоминания и сохраняет заметку.
        """
        data = await state.get_data()
        text = data['text']
        try:
            reminder_time = datetime.strptime(message.text, '%Y-%m-%d %H:%M')
        except ValueError:
            await message.answer("Неверный формат даты. Пожалуйста, используйте формат 'YYYY-MM-DD HH:MM'")
            return
        user_id = message.from_user.id

        await self.db.execute('''
            INSERT INTO notes (user_id, text, reminder_time) 
            VALUES ((SELECT id FROM users WHERE telegram_id=$1), $2, $3)
        ''', user_id, text, reminder_time)

        await state.clear()
        await message.answer("Заметка добавлена!")
        print(reminder_time)

    async def list_notes(self, message: Message):
        """
        Показывает список всех заметок пользователя.
        """
        user_id = message.from_user.id
        notes = await self.db.fetch('''
            SELECT text, reminder_time FROM notes 
            WHERE user_id = (SELECT id FROM users WHERE telegram_id=$1) 
            ORDER BY reminder_time ASC
        ''', user_id)
        if notes:
            response = "\n".join([f"{note['text']} - {note['reminder_time']}" for note in notes])
        else:
            response = "У вас нет заметок."
        await message.answer(response)

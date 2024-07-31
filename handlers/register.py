from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from db import Database
import re

class RegisterUser(StatesGroup):
    """
    Стейты для регистрации пользователя.
    """
    name = State()
    email = State()

class RegisterHandler:
    """
    Класс, обрабатывающий регистрацию пользователей в боте.
    """
    def __init__(self, db: Database):
        self.db = db
        self.router = Router()

    def register(self, router: Router):
        """
        Регистрирует хендлеры для команд /start и состояний RegisterUser.
        """
        self.router.message.register(self.start_command, Command(commands=["start"]))
        self.router.message.register(self.process_name, RegisterUser.name)
        self.router.message.register(self.process_email, RegisterUser.email)
        router.include_router(self.router)

    async def start_command(self, message: Message, state: FSMContext):
        """
        Обрабатывает команду /start. Запрашивает имя пользователя, если он не зарегистрирован.
        """
        user_id = message.from_user.id
        user = await self.db.fetchrow('SELECT * FROM users WHERE telegram_id=$1', user_id)
        if not user:
            await message.answer("Добро пожаловать! Пожалуйста, введите ваше имя:")
            await state.set_state(RegisterUser.name)
        else:
            await message.answer("Вы уже зарегистрированы. Используйте команды для работы с заметками.")

    async def process_name(self, message: Message, state: FSMContext):
        """
        Обрабатывает ввод имени пользователя.
        """
        await state.update_data(name=message.text)
        await state.set_state(RegisterUser.email)
        await message.answer("Введите ваш email:")

    async def process_email(self, message: Message, state: FSMContext):
        """
        Обрабатывает ввод email пользователя и завершает регистрацию.
        """
        data = await state.get_data()
        name = data['name']
        email = message.text
        telegram_id = message.from_user.id

        # Валидация email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            await message.answer("Некорректный email. Пожалуйста, введите правильный адрес электронной почты.")
            return

        await self.db.execute('''
            INSERT INTO users (name, email, telegram_id) VALUES ($1, $2, $3)
        ''', name, email, telegram_id)

        await state.clear()
        await message.answer("Вы успешно зарегистрированы!")

from asyncio import run
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_TOKEN
from db import Database
from handlers.register import RegisterHandler
from handlers.notes import NotesHandler
from utils.notifications import NotificationService


class MyTelegramBot:
    """
    Класс для управления Telegram-ботом.

    Инициализирует бот, хранилище состояний, диспетчер, базу данных и службы уведомлений.
    Обрабатывает регистрацию команд и обработчиков сообщений.
    """

    def __init__(self):
        """
        Инициализация бота и всех необходимых компонентов.
        """
        self.bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.storage = MemoryStorage()
        self.dp = Dispatcher(storage=self.storage)
        self.db = Database()
        self.notification_service = NotificationService(self.db, self.bot)
        self.register_handler = RegisterHandler(self.db)
        self.notes_handler = NotesHandler(self.db)

    def register_handlers(self):
        """
        Регистрация обработчиков команд и сообщений.
        """
        self.register_handler.register(self.dp)
        self.notes_handler.register(self.dp)

    async def run(self):
        """
        Запуск бота и необходимых сервисов.
        """
        await self.db.initialize()
        await self.notification_service.start()
        self.register_handlers()
        await self.dp.start_polling(self.bot)


if __name__ == '__main__':
    bot_instance = MyTelegramBot()
    run(bot_instance.run())

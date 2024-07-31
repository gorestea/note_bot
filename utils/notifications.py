import asyncio
from asyncio import create_task
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.sessions import MemorySession
from config import TELETHON_API_ID, TELETHON_API_HASH, API_TOKEN
from db import Database


class NotificationService:
    """
    Сервис уведомлений для отправки напоминаний пользователям.
    """

    def __init__(self, db: Database, bot):
        self.db = db
        self.bot = bot
        self.client = TelegramClient(MemorySession(), TELETHON_API_ID, TELETHON_API_HASH)

    async def start(self):
        """
        Запускает Telethon клиент и задачу проверки напоминаний.
        """
        await self.client.start(bot_token=API_TOKEN)
        create_task(self.check_reminders())

    async def check_reminders(self):
        """
        Периодически проверяет базу данных на наличие предстоящих напоминаний
        и отправляет уведомления пользователям за 10 минут до времени напоминания.
        """
        while True:
            now = datetime.now().replace(second=0, microsecond=0)
            upcoming_time = now + timedelta(minutes=10)

            notes = await self.db.fetch('''
                SELECT u.telegram_id, n.text FROM notes n
                JOIN users u ON n.user_id = u.id
                WHERE n.reminder_time = $1
            ''', upcoming_time)

            if notes:
                for note in notes:
                    await self.bot.send_message(note['telegram_id'], f"Напоминание: {note['text']}")

            await asyncio.sleep(60)

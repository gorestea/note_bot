import asyncpg
from config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT


class Database:
    """
    Класс для управления подключением к базе данных PostgreSQL и выполнения операций с базой данных.
    """

    def __init__(self):
        """
        Инициализация класса Database без активного подключения к базе данных.
        """
        self.pool = None

    async def initialize(self):
        """
        Инициализация пула соединений и создание таблиц в базе данных.
        """
        self.pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT
        )
        await self.create_tables()

    async def create_tables(self):
        """
        Создание таблиц users и notes в базе данных, если они не существуют.
        """
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    telegram_id BIGINT UNIQUE NOT NULL
                );
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    text TEXT NOT NULL,
                    reminder_time TIMESTAMP NOT NULL
                );
            ''')

    """
    Вынесение логики БД
    """
    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                return await conn.execute(query, *args)

    async def fetch(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

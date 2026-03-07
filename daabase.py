import asyncpg
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

class Database:
    def __init__(self):
        self.pool = None

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            min_size=1,
            max_size=10
        )

    async def init_db(self):
        """Создаёт таблицы, если их нет"""
        async with self.pool.acquire() as conn:
            # Таблица пользователей
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    language_code VARCHAR(2) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            # Таблица сообщений
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    message_text TEXT NOT NULL,
                    response_text TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')

    async def get_user_language(self, user_id: int) -> str | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('SELECT language_code FROM users WHERE user_id = $1', user_id)
            return row['language_code'] if row else None

    async def set_user_language(self, user_id: int, language_code: str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (user_id, language_code)
                VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE SET language_code = EXCLUDED.language_code
            ''', user_id, language_code)

    async def save_message(self, user_id: int, message_text: str, response_text: str = None):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO messages (user_id, message_text, response_text)
                VALUES ($1, $2, $3)
            ''', user_id, message_text, response_text)

# Создаём глобальный экземпляр БД
db = Database()
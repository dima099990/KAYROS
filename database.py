import aiosqlite
from datetime import datetime

DB_NAME = "bot_database.db"

async def init_db():
    """Создаёт таблицы, если их нет."""
    async with aiosqlite.connect(DB_NAME) as db:
        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Таблица сообщений
        await db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                role TEXT NOT NULL,  -- 'user' или 'assistant'
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.commit()

async def get_user_language(user_id: int) -> str | None:
    """Возвращает язык пользователя или None, если пользователь не найден."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT language FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def create_user(user_id: int, language: str):
    """Создаёт запись о новом пользователе."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO users (user_id, language) VALUES (?, ?)', (user_id, language))
        await db.commit()

async def save_message(user_id: int, text: str, role: str):
    """Сохраняет сообщение (от пользователя или от бота)."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT INTO messages (user_id, message_text, role) VALUES (?, ?, ?)',
            (user_id, text, role)
        )
        await db.commit()
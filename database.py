import aiosqlite

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
        # Таблица сообщений с каскадным удалением
        await db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_text TEXT NOT NULL,
                role TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        ''')
        # Таблица заказов (обновлённая)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                total_amount REAL,
                payment_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        ''')
        # Таблица позиций заказа
        await db.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                tariff TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price_per_item REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE
            )
        ''')
        # Таблица корзины
        await db.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                user_id INTEGER NOT NULL,
                tariff TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, tariff),
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        ''')
        await db.commit()

# ---------- Пользователи ----------
async def get_user_language(user_id: int) -> str | None:
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT language FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def create_user(user_id: int, language: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO users (user_id, language) VALUES (?, ?)', (user_id, language))
        await db.commit()

async def update_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
        await db.commit()

async def delete_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        await db.commit()

# ---------- Сообщения ----------
async def save_message(user_id: int, text: str, role: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT INTO messages (user_id, message_text, role) VALUES (?, ?, ?)',
            (user_id, text, role)
        )
        await db.commit()

# ---------- Заказы ----------
async def create_order(user_id: int, items: list, total_amount: float) -> int:
    """
    Создаёт заказ и его позиции.
    items: список кортежей (tariff, quantity, price_per_item)
    """
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            'INSERT INTO orders (user_id, status, total_amount) VALUES (?, ?, ?)',
            (user_id, 'pending', total_amount)
        )
        order_id = cursor.lastrowid
        for tariff, quantity, price in items:
            await db.execute(
                'INSERT INTO order_items (order_id, tariff, quantity, price_per_item) VALUES (?, ?, ?, ?)',
                (order_id, tariff, quantity, price)
            )
        await db.commit()
        return order_id

async def update_order_status(order_id: int, status: str, payment_id: str = None):
    async with aiosqlite.connect(DB_NAME) as db:
        if payment_id:
            await db.execute(
                'UPDATE orders SET status = ?, payment_id = ? WHERE id = ?',
                (status, payment_id, order_id)
            )
        else:
            await db.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        await db.commit()

async def get_user_orders(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            'SELECT id, status, total_amount, created_at FROM orders WHERE user_id = ? ORDER BY created_at DESC',
            (user_id,)
        ) as cursor:
            return await cursor.fetchall()

async def get_order_details(order_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM orders WHERE id = ?', (order_id,)) as cursor:
            order = await cursor.fetchone()
        async with db.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,)) as cursor:
            items = await cursor.fetchall()
        return order, items

# ---------- Корзина ----------
async def add_to_cart(user_id: int, tariff: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO cart (user_id, tariff, quantity)
            VALUES (?, ?, 1)
            ON CONFLICT(user_id, tariff) DO UPDATE SET quantity = quantity + 1
        ''', (user_id, tariff))
        await db.commit()

async def remove_from_cart(user_id: int, tariff: str, remove_all: bool = False):
    async with aiosqlite.connect(DB_NAME) as db:
        if remove_all:
            await db.execute('DELETE FROM cart WHERE user_id = ? AND tariff = ?', (user_id, tariff))
        else:
            await db.execute('''
                UPDATE cart SET quantity = quantity - 1
                WHERE user_id = ? AND tariff = ? AND quantity > 1
            ''', (user_id, tariff))
            if db.total_changes == 0:
                await db.execute('DELETE FROM cart WHERE user_id = ? AND tariff = ?', (user_id, tariff))
        await db.commit()

async def get_cart(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT tariff, quantity FROM cart WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchall()

async def clear_cart(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        await db.commit()
import os
from dotenv import load_dotenv
from pathlib import Path

# Явно указываем путь к .env (на всякий случай)
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Отладочный вывод
if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN не найден в .env!")
else:
    print(f"✅ Токен загружен: {BOT_TOKEN[:10]}...")  # покажем только начало

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY не найден в .env!")
else:
    print(f"✅ API ключ загружен: {OPENAI_API_KEY[:10]}...")
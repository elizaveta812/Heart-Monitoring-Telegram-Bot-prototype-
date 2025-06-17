import os
from dotenv import load_dotenv

# загружаем переменные окружения из .env файла
load_dotenv()

# получаем токен из переменной окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# URL FastAPI приложения
API_URL = "http://127.0.0.1:8000"

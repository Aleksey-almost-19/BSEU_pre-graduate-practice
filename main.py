import telebot
import os

def load_env():
    """Читает .env файл вручную"""
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    except FileNotFoundError:
        print("⚠️ Файл .env не найден")

# Загружаем переменные
load_env()

# Получаем токен
TOKEN = os.getenv('TOKEN')

if TOKEN is None:
    print("❌ Ошибка: Токен не найден")
    print("Создайте файл .env с содержанием: TOKEN=ваш_токен")
    exit(1)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Бот работает! ✅")

print("Бот запущен...")
bot.infinity_polling()
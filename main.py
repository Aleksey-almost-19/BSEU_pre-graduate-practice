import telebot
import os
import sys
import time
from telebot import types

print("=" * 60)
print("🤖 BOT FOR BSEU PRE-GRADUATE PRACTICE")
print("=" * 60)

# Ваши ссылки
WEB_APP_URL = "https://bseu-pre-graduate-practice.onrender.com"  # Render хостинг
BOT_LINK = "t.me/FromForBank_bot/WebApp"  # Ссылка от BotFather

def load_env():
    """Читает .env файл вручную"""
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("✅ .env файл загружен")
        return True
    except FileNotFoundError:
        print("❌ Файл .env не найден")
        return False

# Загружаем переменные
if not load_env():
    sys.exit(1)

# Получаем токен
TOKEN = os.getenv('TOKEN')

if TOKEN is None:
    print("❌ Ошибка: Токен не найден в .env")
    sys.exit(1)

print(f"✅ Токен получен: {TOKEN[:10]}...")
print(f"🌐 Web App URL: {WEB_APP_URL}")
print(f"🔗 Bot Link: {BOT_LINK}")

# Создаем бота
try:
    bot = telebot.TeleBot(TOKEN)
    print("✅ Объект бота создан")
except Exception as e:
    print(f"❌ Ошибка создания бота: {e}")
    sys.exit(1)

def setup_menu_button():
    """Устанавливает Menu Button (кнопку меню) для бота"""
    try:
        # Создаем объект MenuButtonWebApp
        menu_button = types.MenuButtonWebApp(
            type="web_app",  # Тип кнопки
            text="🌐 Web App",  # Текст на кнопке
            web_app=types.WebAppInfo(url=WEB_APP_URL)  # Web App URL
        )
        
        # Устанавливаем Menu Button для бота
        bot.set_chat_menu_button(menu_button=menu_button)
        print("✅ Menu Button установлен")
        return True
    except Exception as e:
        print(f"⚠️ Не удалось установить Menu Button: {e}")
        return False

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Обработчик команды /start с кнопкой Web App"""
    
    # Создаем инлайн-клавиатуру
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Кнопка 1: Открыть Web App
    web_app_btn = types.InlineKeyboardButton(
        text="🚀 Открыть Web App",
        web_app=types.WebAppInfo(url=WEB_APP_URL)
    )
    
    # Кнопка 2: Прямая ссылка
    direct_link_btn = types.InlineKeyboardButton(
        text="🔗 Открыть через ссылку",
        url=BOT_LINK
    )
    
    # Кнопка 3: Проверить сайт
    check_site_btn = types.InlineKeyboardButton(
        text="🌐 Проверить сайт",
        url=WEB_APP_URL
    )
    
    markup.add(web_app_btn, direct_link_btn, check_site_btn)
    
    welcome_text = f"""
🎓 **BSEU Pre-Graduate Practice Bot**

👋 Привет, {message.from_user.first_name}!

Я бот для преддипломной практики БГЭУ.

**Команды:**
/setup - настроить Menu Button
/webapp - открыть Web App
/link - получить ссылки
"""
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )
    
    print(f"📨 Приветствие отправлено: {message.from_user.username}")

@bot.message_handler(commands=['setup'])
def setup_command(message):
    """Установка Menu Button"""
    if setup_menu_button():
        bot.reply_to(message, 
            "✅ **Menu Button установлен!**\n\n"
            "Теперь рядом с полем ввода появится кнопка '🌐 Web App'.\n"
            "Работает как у @BotFather.")
    else:
        bot.reply_to(message,
            "⚠️ **Не удалось установить Menu Button.**\n\n"
            "Используйте кнопки в сообщениях или прямую ссылку:\n"
            f"🔗 {BOT_LINK}")

@bot.message_handler(commands=['webapp'])
def open_webapp(message):
    """Быстрое открытие Web App"""
    markup = types.InlineKeyboardMarkup()
    
    web_app_btn = types.InlineKeyboardButton(
        text="🌐 Открыть Web App",
        web_app=types.WebAppInfo(url=WEB_APP_URL)
    )
    
    markup.add(web_app_btn)
    
    bot.send_message(
        message.chat.id,
        "Нажмите кнопку, чтобы открыть Web App:",
        reply_markup=markup
    )

@bot.message_handler(commands=['link'])
def send_links(message):
    """Отправить все ссылки"""
    links_text = f"""
🔗 **Все ссылки проекта:**

**🌐 Web App (основная):**
• URL: `{WEB_APP_URL}`
• Для открытия в Telegram

**🤖 Прямая ссылка от BotFather:**
• {BOT_LINK}
• Можно поделиться с другими

**📱 Быстрые кнопки:**
• Используйте команду /webapp
• Или нажмите кнопку в меню /start

**💡 Как использовать:**
1. Нажмите кнопку в боте
2. Или откройте ссылку в браузере
3. Или отправьте ссылку друзьям
"""
    
    # Кнопки для быстрого доступа
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    btn1 = types.InlineKeyboardButton(
        "🌐 Открыть в Telegram",
        web_app=types.WebAppInfo(url=WEB_APP_URL)
    )
    
    btn2 = types.InlineKeyboardButton(
        "🔗 Копировать ссылку",
        callback_data="copy_link"
    )
    
    btn3 = types.InlineKeyboardButton(
        "📋 Открыть в браузере",
        url=WEB_APP_URL
    )
    
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(
        message.chat.id,
        links_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data == "copy_link")
def copy_link_callback(call):
    """Обработчик кнопки копирования ссылки"""
    bot.answer_callback_query(
        call.id,
        f"Ссылка скопирована в буфер!\n{WEB_APP_URL}",
        show_alert=True
    )

@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    """Обработка данных из Web App"""
    try:
        data = message.web_app_data.data
        button_text = message.web_app_data.button_text
        
        response = f"""
🎉 **Данные получены из Web App!**

**От:** {message.from_user.first_name}
**Кнопка:** {button_text}
**Данные:** `{data[:100]}{'...' if len(data) > 100 else ''}`

✅ Web App успешно отправляет данные боту!
"""
        
        bot.send_message(message.chat.id, response, parse_mode='Markdown')
        print(f"📤 Данные от Web App: {data[:50]}...")
        
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Ошибка обработки данных: {str(e)}",
            parse_mode='Markdown'
        )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Обработка всех сообщений"""
    
    # Быстрые команды
    quick_commands = {
        'сайт': WEB_APP_URL,
        'webapp': WEB_APP_URL,
        'ссылка': BOT_LINK,
        'link': BOT_LINK,
        'бот': BOT_LINK,
        'bot': BOT_LINK,
        'открыть': 'используйте /webapp',
        'open': 'use /webapp'
    }
    
    text_lower = message.text.lower()
    
    if text_lower in quick_commands:
        response = f"""
🔍 **Быстрый ответ:**

Запрос: `{message.text}`

**Результат:**
{quick_commands[text_lower]}

**Что сделать:**
• Нажмите /webapp для открытия
• Или /link для всех ссылок
• Или /start для меню
"""
        bot.reply_to(message, response, parse_mode='Markdown')
    else:
        # Показываем меню помощи
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        
        btn1 = types.KeyboardButton("🌐 Web App")
        btn2 = types.KeyboardButton("🔗 Ссылка")
        btn3 = types.KeyboardButton("❓ Помощь")
        
        markup.add(btn1, btn2, btn3)
        
        help_text = f"""
💬 Вы написали: `{message.text}`

🤖 **BSEU Pre-Graduate Practice Bot**

**Быстрые команды:**
• Напишите `сайт` - получить URL Web App
• Напишите `ссылка` - получить прямую ссылку
• Напишите `бот` - информация о боте

**Или используйте кнопки ниже:**

**Или команды:**
/start - главное меню
/webapp - открыть Web App
/link - все ссылки
/help - помощь

**Ссылка от BotFather:** `{BOT_LINK}`
"""
        
        bot.send_message(
            message.chat.id,
            help_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )

# Обработчик reply-кнопок
@bot.message_handler(func=lambda message: message.text in ["🌐 Web App", "🔗 Ссылка", "❓ Помощь"])
def handle_reply_buttons(message):
    """Обработчик reply-кнопок"""
    
    if message.text == "🌐 Web App":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(
            "🚀 Открыть Web App",
            web_app=types.WebAppInfo(url=WEB_APP_URL)
        )
        markup.add(btn)
        bot.send_message(
            message.chat.id,
            "Нажмите кнопку, чтобы открыть Web App:",
            reply_markup=markup
        )
        
    elif message.text == "🔗 Ссылка":
        bot.send_message(
            message.chat.id,
            f"🔗 **Прямая ссылка от BotFather:**\n\n`{BOT_LINK}`\n\n"
            "Эту ссылку можно отправлять другим пользователям.\n"
            "При нажатии откроется Web App в Telegram.",
            parse_mode='Markdown'
        )
        
    elif message.text == "❓ Помощь":
        bot.send_message(
            message.chat.id,
            "❓ **Помощь по использованию бота:**\n\n"
            "1. **Web App** - основное веб-приложение\n"
            "2. **Прямая ссылка** - для расшаривания\n"
            "3. **Menu Button** - кнопка рядом с полем ввода\n\n"
            "**Команды:**\n"
            "/setup - настроить Menu Button\n"
            "/link - все ссылки\n"
            "/webapp - быстрое открытие",
            parse_mode='Markdown'
        )

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("⚙️  НАСТРОЙКА СИСТЕМЫ")
    print("=" * 60)
    
    # Очищаем вебхук
    try:
        bot.delete_webhook()
        print("✅ Вебхук очищен")
    except:
        pass
    
    time.sleep(1)
    
    # Проверяем подключение
    try:
        bot_info = bot.get_me()
        print(f"✅ Бот подключен: @{bot_info.username}")
        print(f"📛 Имя бота: {bot_info.first_name}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        sys.exit(1)
    
    # Устанавливаем Menu Button
    print("\n🔄 Установка Menu Button...")
    if setup_menu_button():
        print("✅ Menu Button установлен")
    else:
        print("⚠️ Используйте команду /setup для ручной настройки")
    
    print("\n" + "=" * 60)
    print("🎯 ИНФОРМАЦИЯ О ПРОЕКТЕ")
    print("=" * 60)
    print(f"🌐 Web App URL: {WEB_APP_URL}")
    print(f"🔗 Bot Link: {BOT_LINK}")
    print(f"🤖 Bot: @{bot_info.username}")
    print("📚 Назначение: Преддипломная практика БГЭУ")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("🚀 БОТ ЗАПУЩЕН!")
    print("=" * 60)
    print("📱 Отправьте /start в Telegram")
    print("🌐 Используйте /webapp для открытия Web App")
    print("🔗 Используйте /link для получения ссылок")
    print("⏹️  Ctrl+C для остановки")
    print("=" * 60 + "\n")
    
    # Запускаем polling
    try:
        bot.infinity_polling(
            timeout=30,
            long_polling_timeout=15,
            skip_pending=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Бот остановлен")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        print("✅ Работа завершена")
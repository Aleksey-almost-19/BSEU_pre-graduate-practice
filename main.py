import telebot
import os
import sys
import time
import requests
from telebot import types

print("=" * 60)
print("🤖 BOT FOR BSEU PRE-GRADUATE PRACTICE")
print("=" * 60)

# Ваши ссылки
WEB_APP_URL = "https://tambra-vitrifiable-jonnie.ngrok-free.dev/"
ADMIN_URL = "https://tambra-vitrifiable-jonnie.ngrok-free.dev/admin.html"  # Админка
BOT_LINK = "t.me/FromForBank_bot/WebApp"  # Ссылка от BotFather

# Telegram ID администратора (ваш)
ADMIN_USER_ID = 898880921  # ✅ ВАШ ID

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
            type="web_app",
            text="🌐 Web App",
            web_app=types.WebAppInfo(url=WEB_APP_URL)
        )
        
        # Устанавливаем Menu Button для бота
        bot.set_chat_menu_button(menu_button=menu_button)
        print("✅ Menu Button установлен")
        return True
    except Exception as e:
        print(f"⚠️ Не удалось установить Menu Button: {e}")
        return False

def is_admin(user_id):
    """Проверяет, является ли пользователь администратором"""
    return user_id == ADMIN_USER_ID

def get_unprocessed_requests():
    """Получает количество необработанных заявок из API"""
    try:
        response = requests.get(f"{WEB_APP_URL}/api/contact-requests", timeout=5)
        if response.status_code == 200:
            requests_data = response.json()
            # Считаем заявки со статусом 'new'
            unprocessed = sum(1 for req in requests_data if req.get('status') == 'new')
            return unprocessed, len(requests_data)
        else:
            return None, None
    except Exception as e:
        print(f"Ошибка получения заявок: {e}")
        return None, None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Обработчик команды /start с кнопкой Web App"""
    
    # Создаем инлайн-клавиатуру (ТОЛЬКО ОДНА КНОПКА)
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Единственная кнопка: Открыть Web App
    web_app_btn = types.InlineKeyboardButton(
        text="🚀 Открыть Web App",
        web_app=types.WebAppInfo(url=WEB_APP_URL)
    )
    
    markup.add(web_app_btn)
    
    welcome_text = (
        "🎓 **BSEU Pre-Graduate Practice Bot**\n\n"
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я бот для преддипломной практики БГЭУ.\n\n"
        "**Доступные команды:**\n"
        "/webapp - открыть Web App"
    )
    
    if is_admin(message.from_user.id):
        welcome_text += "\n/admin - админ-панель\n/status - статистика заявок"
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )
    
    print(f"📨 Приветствие отправлено: {message.from_user.username}")

@bot.message_handler(commands=['status'])
def status_command(message):
    """Команда для просмотра статуса заявок (только для админа)"""
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ **У вас нет доступа к этой команде.**", parse_mode='Markdown')
        return
    
    # Отправляем сообщение о загрузке
    status_msg = bot.reply_to(message, "⏳ **Получаю данные о заявках...**", parse_mode='Markdown')
    
    # Получаем данные из API
    unprocessed, total = get_unprocessed_requests()
    
    if unprocessed is None:
        bot.edit_message_text(
            "❌ **Ошибка подключения к API.**\n\n"
            "Не удалось получить данные о заявках.\n"
            "Проверьте, запущен ли сервер.",
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            parse_mode='Markdown'
        )
        return
    
    # Создаем клавиатуру для быстрого перехода в админку
    markup = types.InlineKeyboardMarkup()
    admin_btn = types.InlineKeyboardButton(
        text="🔐 Перейти в админ-панель",
        web_app=types.WebAppInfo(url=ADMIN_URL)
    )
    markup.add(admin_btn)
    
    status_text = (
        "📊 **СТАТИСТИКА ЗАЯВОК**\n\n"
        f"👑 Администратор: @{message.from_user.username}\n\n"
        "**📌 Текущий статус:**\n"
        f"• 🆕 **Необработанных заявок:** `{unprocessed}`\n"
        f"• 📦 **Всего заявок:** `{total}`\n\n"
        "**📈 Детализация:**\n"
        f"• {'🔴 Требуют внимания!' if unprocessed > 0 else '✅ Все заявки обработаны'}"
    )
    
    bot.edit_message_text(
        status_text,
        chat_id=message.chat.id,
        message_id=status_msg.message_id,
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    """Команда для открытия админ-панели (только для админа) - УПРОЩЕНО"""
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "❌ **У вас нет доступа к админ-панели.**", parse_mode='Markdown')
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # Только одна кнопка для открытия админки
    admin_btn = types.InlineKeyboardButton(
        text="🔐 Открыть админ-панель",
        web_app=types.WebAppInfo(url=ADMIN_URL)
    )
    
    markup.add(admin_btn)
    
    admin_text = (
        "🔐 **Админ-панель AurumBank**\n\n"
        f"👤 Администратор: @{message.from_user.username}\n\n"
        "Нажмите кнопку ниже для доступа:"
    )
    
    bot.send_message(
        message.chat.id,
        admin_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['webapp'])
def open_webapp(message):
    """Быстрое открытие Web App"""
    markup = types.InlineKeyboardMarkup()
    
    web_app_btn = types.InlineKeyboardButton(
        text="🚀 Открыть Web App",
        web_app=types.WebAppInfo(url=WEB_APP_URL)
    )
    
    markup.add(web_app_btn)
    
    bot.send_message(
        message.chat.id,
        "Нажмите кнопку, чтобы открыть Web App:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "show_status")
def status_callback(call):
    """Обработчик кнопки показа статуса"""
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ У вас нет доступа", show_alert=True)
        return
    
    # Получаем данные
    unprocessed, total = get_unprocessed_requests()
    
    if unprocessed is None:
        bot.answer_callback_query(
            call.id,
            "❌ Ошибка подключения к API",
            show_alert=True
        )
        return
    
    status_text = (
        f"📊 СТАТИСТИКА ЗАЯВОК\n\n"
        f"• 🆕 Необработанных: {unprocessed}\n"
        f"• 📦 Всего заявок: {total}\n"
        f"• {'🔴 Требуют внимания!' if unprocessed > 0 else '✅ Все хорошо'}"
    )
    
    bot.answer_callback_query(
        call.id,
        status_text,
        show_alert=True
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Обработка всех сообщений"""
    
    # Показываем меню помощи
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    # Только одна reply-кнопка
    webapp_btn = types.KeyboardButton("🚀 Web App")
    buttons = [webapp_btn]
    
    # Для админа добавляем дополнительные кнопки
    if is_admin(message.from_user.id):
        admin_btn = types.KeyboardButton("🔐 Админка")
        status_btn = types.KeyboardButton("📊 Статистика")
        buttons.extend([admin_btn, status_btn])
    
    markup.add(*buttons)
    
    help_text = (
        f"💬 Вы написали: `{message.text}`\n\n"
        "🤖 **BSEU Pre-Graduate Practice Bot**\n\n"
        "**Команды:**\n"
        "🚀 /webapp - открыть Web App"
    )
    
    if is_admin(message.from_user.id):
        help_text += "\n🔐 /admin - админ-панель\n📊 /status - статистика заявок"
    
    help_text += "\n\n**Или используйте кнопки ниже:**"
    
    bot.send_message(
        message.chat.id,
        help_text,
        reply_markup=markup,
        parse_mode='Markdown'
    )

# Обработчик reply-кнопок
@bot.message_handler(func=lambda message: message.text in ["🚀 Web App", "🔐 Админка", "📊 Статистика"])
def handle_reply_buttons(message):
    """Обработчик reply-кнопок"""
    
    if message.text == "🚀 Web App":
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
        
    elif message.text == "🔐 Админка":
        if not is_admin(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "❌ У вас нет доступа к админ-панели.",
                parse_mode='Markdown'
            )
            return
        
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(
            "🔐 Открыть админ-панель",
            web_app=types.WebAppInfo(url=ADMIN_URL)
        )
        markup.add(btn)
        
        bot.send_message(
            message.chat.id,
            "Нажмите кнопку, чтобы открыть админ-панель:",
            reply_markup=markup
        )
        
    elif message.text == "📊 Статистика":
        if not is_admin(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "❌ У вас нет доступа к статистике.",
                parse_mode='Markdown'
            )
            return
        
        # Используем ту же логику, что и в /status
        unprocessed, total = get_unprocessed_requests()
        
        if unprocessed is None:
            bot.send_message(
                message.chat.id,
                "❌ **Ошибка подключения к API**",
                parse_mode='Markdown'
            )
            return
        
        markup = types.InlineKeyboardMarkup()
        admin_btn = types.InlineKeyboardButton(
            text="🔐 Перейти в админку",
            web_app=types.WebAppInfo(url=ADMIN_URL)
        )
        markup.add(admin_btn)
        
        status_text = (
            "📊 **СТАТИСТИКА ЗАЯВОК**\n\n"
            f"• 🆕 **Необработанных:** `{unprocessed}`\n"
            f"• 📦 **Всего заявок:** `{total}`\n\n"
            f"**Статус:** {'🔴 Требуют внимания!' if unprocessed > 0 else '✅ Все обработаны'}"
        )
        
        bot.send_message(
            message.chat.id,
            status_text,
            reply_markup=markup,
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
    print(f"🔐 Admin URL: {ADMIN_URL}")
    print(f"🔗 Bot Link: {BOT_LINK}")
    print(f"🤖 Bot: @{bot_info.username}")
    print(f"👑 Admin ID: {ADMIN_USER_ID}")
    print("📚 Назначение: Преддипломная практика БГЭУ")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("🚀 БОТ ЗАПУЩЕН!")
    print("=" * 60)
    print("📱 Отправьте /start в Telegram")
    print("🌐 Используйте /webapp для открытия Web App")
    print("👑 Админ-команды: /admin, /status")
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
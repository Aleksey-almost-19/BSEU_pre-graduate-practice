import http.server
import socketserver
import os
import json
from datetime import datetime
import mimetypes

PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    """Кастомный обработчик с поддержкой index.html"""
    
    def do_GET(self):
        # Если запрашивают корень, показываем index.html
        if self.path == '/':
            self.path = '/index.html'
        
        # Полный путь к файлу
        file_path = self.path.lstrip('/')
        
        
        
        

def main():
    """Основная функция"""
    
    print("=" * 60)
    print("🌐 ЗАПУСК ВЕБ-СЕРВЕРА НА PYTHON")
    print("=" * 60)
    
    
    
    print(f"\n📂 Рабочая папка: {os.getcwd()}")
    print(f"🌐 Сервер доступен по адресу: http://localhost:{PORT}")
    print(f"📄 Главная страница: http://localhost:{PORT}/index.html")
    print("\n📋 Доступные файлы:")
    
    # Показываем файлы в текущей папке
    for file in os.listdir('.'):
        if os.path.isfile(file):
            size = os.path.getsize(file)
            print(f"  📄 {file} ({size} байт)")
    
    print("\n" + "=" * 60)
    print("⚡ Сервер запущен...")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("=" * 60)
    
    try:
        # Запускаем сервер
        with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Сервер остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
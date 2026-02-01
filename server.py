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
        
        # Если файла нет
        if not os.path.exists(file_path) or file_path == '':
            self.send_response(404)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            error_html = '''
            <!DOCTYPE html>
            <html>
            <head><title>404 - Не найдено</title></head>
            <body>
                <h1>404 - Файл не найден</h1>
                <p>Создайте файл index.html в этой папке:</p>
                <pre>''' + os.getcwd() + '''</pre>
            </body>
            </html>'''
            self.wfile.write(error_html.encode('utf-8'))
            return
        
        # Определяем Content-Type по расширению файла
        content_type = mimetypes.guess_type(file_path)[0] or 'text/plain'
        
        # Отправляем файл
        self.send_response(200)
        self.send_header('Content-type', content_type)
        if content_type.startswith('text/'):
            self.send_header('Content-type', content_type + '; charset=utf-8')
        self.end_headers()
        
        try:
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
    
    def log_message(self, format, *args):
        """Красивое логирование"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {self.address_string()} - {format % args}")

def create_index_html_if_needed():
    """Создает index.html если его нет"""
    if not os.path.exists('index.html'):
        print("📝 Создаю index.html...")
        html_content = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Мой сервер</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 15px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }
        h1 { 
            color: #333; 
            margin-bottom: 20px;
            font-size: 2.5em;
        }
        .status {
            background: #4CAF50;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            font-size: 1.2em;
        }
        .info {
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 15px 0;
            text-align: left;
            border-radius: 0 5px 5px 0;
        }
        .btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #0056b3;
        }
        .file-list {
            margin-top: 20px;
            text-align: left;
        }
        .file-list li {
            padding: 8px;
            border-bottom: 1px solid #eee;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Сервер работает!</h1>
        
        <div class="status">
            ✅ Сервер успешно запущен на Python
        </div>
        
        <div class="info">
            <p><strong>Адрес:</strong> http://localhost:8000</p>
            <p><strong>Папка:</strong> ''' + os.getcwd().replace('\\', '/') + '''</p>
            <p><strong>Сервер:</strong> Python HTTP Server</p>
            <p><strong>Время запуска:</strong> ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
        </div>
        
        <div>
            <button class="btn" onclick="showAlert()">Тест JavaScript</button>
            <button class="btn" onclick="loadFiles()">Показать файлы</button>
        </div>
        
        <div class="file-list">
            <h3>Файлы в папке:</h3>
            <ul id="files"></ul>
        </div>
        
        <div style="margin-top: 30px; color: #666; font-size: 0.9em;">
            <p>Сервер работает без Flask на чистом Python</p>
        </div>
    </div>
    
    <script>
        function showAlert() {
            alert('JavaScript работает! Сервер функционирует корректно.');
        }
        
        function loadFiles() {
            fetch('/?list')
                .then(response => response.text())
                .then(html => {
                    // Простой парсинг для показа файлов
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const links = doc.querySelectorAll('a');
                    const fileList = document.getElementById('files');
                    fileList.innerHTML = '';
                    
                    links.forEach(link => {
                        if (link.href && !link.href.includes('?')) {
                            const li = document.createElement('li');
                            li.innerHTML = `📄 <a href="${link.href}">${link.textContent}</a>`;
                            fileList.appendChild(li);
                        }
                    });
                });
        }
        
        // Автоматически загружаем список файлов при загрузке страницы
        window.onload = loadFiles;
        
        console.log('Страница загружена!');
    </script>
</body>
</html>'''
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        return True
    return False

def main():
    """Основная функция"""
    
    print("=" * 60)
    print("🌐 ЗАПУСК ВЕБ-СЕРВЕРА НА PYTHON")
    print("=" * 60)
    
    # Создаем index.html если нужно
    created = create_index_html_if_needed()
    if created:
        print("✅ index.html создан")
    
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
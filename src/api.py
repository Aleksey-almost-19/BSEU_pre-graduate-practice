from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# ===========================================
# 1. ОТДАЧА HTML СТРАНИЦ
# ===========================================

@app.get("/")
async def serve_index():
    return FileResponse("index.html")

@app.get("/loans.html")
async def serve_loans():
    return FileResponse("loans.html")

@app.get("/consumer_loans.html")
async def serve_consumer_loans():
    return FileResponse("consumer_loans.html")

# ===========================================
# 2. ПОДКЛЮЧЕНИЕ СТАТИЧЕСКИХ ФАЙЛОВ (CSS, JS, IMG)
# ===========================================

# Монтируем папки со статикой
app.mount("/style", StaticFiles(directory="style"), name="style")
app.mount("/javascript", StaticFiles(directory="javascript"), name="javascript")
app.mount("/img", StaticFiles(directory="img"), name="img")

# ===========================================
# 3. API ЭНДПОИНТЫ (ВАШ БЭКЕНД)
# ===========================================

@app.get("/api/consumer-loans")
async def get_consumer_loans():
    # Здесь ваш код для работы с БД
    return []

# Для обратной совместимости (если нужен JSON на корневом пути)
@app.get("/api/status")
async def api_status():
    return {"message": "AurumBank API is working!"}
@app.get("/index.html")
async def serve_index_html():
    return FileResponse("index.html")
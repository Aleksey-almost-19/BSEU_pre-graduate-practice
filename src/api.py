from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Отдаём index.html по корневому пути
@app.get("/")
async def root():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return Response(content=html_content, media_type="text/html")
    except FileNotFoundError:
        return {"message": "AurumBank API is working!"}

# API эндпоинты
@app.get("/api/consumer-loans")
async def get_consumer_loans():
    # ваш код
    return []

# Подключаем статические файлы (CSS, JS, картинки)
app.mount("/style", StaticFiles(directory="style"), name="style")
app.mount("/javascript", StaticFiles(directory="javascript"), name="javascript")
app.mount("/img", StaticFiles(directory="img"), name="img")
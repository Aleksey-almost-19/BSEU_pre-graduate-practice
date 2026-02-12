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
@app.get("/api/seed-database")
async def seed_database():
    """Временный эндпоинт для добавления тестовых данных"""
    from sqlalchemy import text
    
    try:
        async with async_session_factory() as session:
            # Проверяем, есть ли данные
            result = await session.execute(text("SELECT COUNT(*) FROM consumer_loans"))
            count = result.scalar()
            
            if count == 0:
                await session.execute(text("""
                    INSERT INTO consumer_loans (name, rate, term, amount, advantage, details) VALUES
                    ('Кредит на любые цели', 'от 11.9%', 'до 7 лет', 'до 15 000 BYN', 
                     'Без справок о доходах, решение за 15 минут', 
                     'Кредит без залога и поручителей. Минимальный пакет документов — только паспорт.'),
                    
                    ('Кредит для зарплатных клиентов', 'от 10.5%', 'до 5 лет', 'до 20 000 BYN', 
                     'Специальные условия для зарплатных клиентов', 
                     'Для клиентов, получающих зарплату на карту Аурумбанка. Сниженная процентная ставка.'),
                    
                    ('Рефинансирование кредитов', 'от 11.5%', 'до 10 лет', 'до 50 000 BYN', 
                     'Объедините несколько кредитов в один', 
                     'Рефинансирование кредитов других банков. Снижение ежемесячного платежа.'),
                    
                    ('Экспресс-кредит', 'от 13.9%', 'до 3 лет', 'до 5 000 BYN', 
                     'Решение за 5 минут, деньги сразу', 
                     'Микрокредит на неотложные нужды. Быстрое оформление через интернет-банкинг.'),
                    
                    ('Кредит на образование', 'от 9.9%', 'до 11 лет', 'до 25 000 BYN', 
                     'Льготный период на время обучения', 
                     'Кредит на оплату обучения в вузах и колледжах. Отсрочка погашения основного долга.')
                """))
                await session.commit()
                return {"status": "success", "message": "✅ Тестовые кредиты добавлены!", "count": 5}
            else:
                return {"status": "info", "message": f"ℹ️ В базе уже есть {count} записей", "count": count}
                
    except Exception as e:
        return {"status": "error", "message": str(e)}
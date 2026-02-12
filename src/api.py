from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import text
import os
import sys

# ===========================================
# ВАЖНО: ИМПОРТЫ ИЗ ВАШЕГО ПРОЕКТА
# ===========================================
sys.path.append(os.path.dirname(__file__))
from database import async_session_factory  # ← ЭТО КЛЮЧЕВОЙ ИМПОРТ!
from sqlalchemy import text

app = FastAPI()

# ===========================================
# 1. ОТДАЧА HTML СТРАНИЦ
# ===========================================

@app.get("/")
async def serve_index():
    return FileResponse("index.html")

@app.get("/index.html")
async def serve_index_html():
    return FileResponse("index.html")

@app.get("/loans.html")
async def serve_loans():
    return FileResponse("loans.html")

@app.get("/consumer_loans.html")
async def serve_consumer_loans():
    return FileResponse("consumer_loans.html")

# ===========================================
# 2. СТАТИЧЕСКИЕ ФАЙЛЫ
# ===========================================

app.mount("/style", StaticFiles(directory="style"), name="style")
app.mount("/javascript", StaticFiles(directory="javascript"), name="javascript")
app.mount("/img", StaticFiles(directory="img"), name="img")

# ===========================================
# 3. ЭНДПОИНТ ДЛЯ ДОБАВЛЕНИЯ ТЕСТОВЫХ ДАННЫХ
# ===========================================

@app.get("/api/seed-database")
async def seed_database():
    """Добавить тестовые кредиты в базу данных"""
    try:
        async with async_session_factory() as session:
            # Проверяем, есть ли уже данные
            result = await session.execute(text("SELECT COUNT(*) FROM consumer_loans"))
            count = result.scalar()
            
            if count == 0:
                # Добавляем тестовые кредиты
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
                     'Рефинансирование кредитов других банков. Снижение ежемесячного платежа.')
                """))
                await session.commit()
                return {
                    "status": "success", 
                    "message": "✅ Тестовые кредиты успешно добавлены!",
                    "count": 3
                }
            else:
                return {
                    "status": "info", 
                    "message": f"ℹ️ В базе уже есть {count} записей",
                    "count": count
                }
                
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "type": type(e).__name__
        }

# ===========================================
# 4. ОСНОВНОЙ API ЭНДПОИНТ ДЛЯ КРЕДИТОВ
# ===========================================

@app.get("/api/consumer-loans")
async def get_consumer_loans():
    """Получить все кредиты из базы данных"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(
                text("SELECT id, name, rate, term, amount, advantage, details FROM consumer_loans ORDER BY id")
            )
            rows = result.mappings().all()
            return [dict(row) for row in rows]
            
    except Exception as e:
        print(f"Error: {e}")
        return []

# ===========================================
# 5. СТАТУС API
# ===========================================

@app.get("/api/status")
async def api_status():
    """Проверка статуса API"""
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {type(e).__name__}"
    
    return {
        "message": "AurumBank API is working!",
        "database": db_status,
        "version": "1.0.0"
    }
@app.get("/api/create-tables")
async def create_tables():
    """Создать таблицу consumer_loans в базе данных"""
    from sqlalchemy import text
    
    try:
        async with async_session_factory() as session:
            # SQL для создания таблицы
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS consumer_loans (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    rate VARCHAR(50) NOT NULL,
                    term VARCHAR(50) NOT NULL,
                    amount VARCHAR(50) NOT NULL,
                    advantage TEXT NOT NULL,
                    details TEXT NOT NULL
                )
            """))
            await session.commit()
            
            return {"status": "success", "message": "✅ Таблица consumer_loans создана!"}
    except Exception as e:
        return {"status": "error", "message": str(e), "type": type(e).__name__}
    
class LoanCreate(BaseModel):
    name: str
    rate: str
    term: str
    amount: str
    advantage: str
    details: str


# 1. ДОБАВИТЬ НОВЫЙ КРЕДИТ
@app.post("/api/consumer-loans")
async def add_loan(loan: LoanCreate):
    try:
        async with async_session_factory() as session:
            await session.execute(text("""
                INSERT INTO consumer_loans (name, rate, term, amount, advantage, details)
                VALUES (:name, :rate, :term, :amount, :advantage, :details)
            """), loan.model_dump())
            await session.commit()
            return {"status": "success", "message": "✅ Кредит добавлен"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 2. УДАЛИТЬ КРЕДИТ
@app.delete("/api/consumer-loans/{loan_id}")
async def delete_loan(loan_id: int):
    try:
        async with async_session_factory() as session:
            result = await session.execute(text("""
                DELETE FROM consumer_loans WHERE id = :id
            """), {"id": loan_id})
            await session.commit()
            if result.rowcount == 0:
                return {"status": "error", "message": "❌ Кредит не найден"}
            return {"status": "success", "message": "✅ Кредит удален"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 3. ПОЛУЧИТЬ КРЕДИТ ПО ID (ОПЦИОНАЛЬНО)
@app.get("/api/consumer-loans/{loan_id}")
async def get_loan(loan_id: int):
    async with async_session_factory() as session:
        result = await session.execute(
            text("SELECT * FROM consumer_loans WHERE id = :id"),
            {"id": loan_id}
        )
        loan = result.mappings().first()
        if not loan:
            return {"status": "error", "message": "❌ Кредит не найден"}
        return dict(loan)        
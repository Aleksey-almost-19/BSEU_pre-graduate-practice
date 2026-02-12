from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import text
import os
import sys

# ===========================================
# ИМПОРТЫ ИЗ ПРОЕКТА
# ===========================================
sys.path.append(os.path.dirname(__file__))
from database import async_session_factory

app = FastAPI()

# ===========================================
# МОДЕЛИ ДАННЫХ
# ===========================================

class LoanCreate(BaseModel):
    name: str
    rate: str
    term: str
    amount: str
    advantage: str
    details: str

# ===========================================
# ОТДАЧА HTML СТРАНИЦ
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

@app.get("/admin.html")
async def serve_admin():
    return FileResponse("admin.html")

# ===========================================
# СТАТИЧЕСКИЕ ФАЙЛЫ
# ===========================================

app.mount("/style", StaticFiles(directory="style"), name="style")
app.mount("/javascript", StaticFiles(directory="javascript"), name="javascript")
app.mount("/img", StaticFiles(directory="img"), name="img")

# ===========================================
# УПРАВЛЕНИЕ БАЗОЙ ДАННЫХ
# ===========================================

@app.get("/api/create-tables")
async def create_tables():
    """Создать таблицу consumer_loans"""
    try:
        async with async_session_factory() as session:
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
        return {"status": "error", "message": str(e)}

@app.get("/api/seed-database")
async def seed_database():
    """Добавить тестовые кредиты"""
    try:
        async with async_session_factory() as session:
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
                     'Рефинансирование кредитов других банков. Снижение ежемесячного платежа.')
                """))
                await session.commit()
                return {"status": "success", "message": "✅ Тестовые кредиты добавлены!", "count": 3}
            else:
                return {"status": "info", "message": f"ℹ️ В базе уже есть {count} записей", "count": count}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ===========================================
# API ДЛЯ КРЕДИТОВ (CRUD)
# ===========================================

# ПОЛУЧИТЬ ВСЕ КРЕДИТЫ
@app.get("/api/consumer-loans")
async def get_all_loans():
    """Получить все кредиты"""
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

# ПОЛУЧИТЬ КРЕДИТ ПО ID
@app.get("/api/consumer-loans/{loan_id}")
async def get_loan(loan_id: int):
    """Получить кредит по ID"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(
                text("SELECT * FROM consumer_loans WHERE id = :id"),
                {"id": loan_id}
            )
            loan = result.mappings().first()
            if not loan:
                raise HTTPException(status_code=404, detail="Кредит не найден")
            return dict(loan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ДОБАВИТЬ НОВЫЙ КРЕДИТ
@app.post("/api/consumer-loans")
async def create_loan(loan: LoanCreate):
    """Добавить новый кредит"""
    try:
        async with async_session_factory() as session:
            await session.execute(text("""
                INSERT INTO consumer_loans (name, rate, term, amount, advantage, details)
                VALUES (:name, :rate, :term, :amount, :advantage, :details)
            """), loan.model_dump())
            await session.commit()
            return {"status": "success", "message": "✅ Кредит успешно добавлен"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ОБНОВИТЬ КРЕДИТ
@app.put("/api/consumer-loans/{loan_id}")
async def update_loan(loan_id: int, loan: LoanCreate):
    """Обновить существующий кредит"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(text("""
                UPDATE consumer_loans 
                SET name = :name, rate = :rate, term = :term, amount = :amount,
                    advantage = :advantage, details = :details
                WHERE id = :id
            """), {**loan.model_dump(), "id": loan_id})
            await session.commit()
            
            if result.rowcount == 0:
                return {"status": "error", "message": "❌ Кредит не найден"}
            return {"status": "success", "message": "✅ Кредит обновлен"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# УДАЛИТЬ КРЕДИТ
@app.delete("/api/consumer-loans/{loan_id}")
async def delete_loan(loan_id: int):
    """Удалить кредит"""
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

# ===========================================
# СТАТУС API
# ===========================================

@app.get("/api/status")
async def api_status():
    """Проверка статуса API и БД"""
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {type(e).__name__}"
    
    return {
        "message": "AurumBank API is working!",
        "database": db_status,
        "version": "2.0.0"
    }
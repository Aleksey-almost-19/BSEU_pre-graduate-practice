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

@app.get("/api/create-mortgage-table")
async def create_mortgage_table():
    """Создать таблицу для ипотечных кредитов"""
    try:
        async with async_session_factory() as session:
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS mortgage_loans (
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
            return {"status": "success", "message": "✅ Таблица mortgage_loans создана!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/create-preferential-table")
async def create_preferential_table():
    """Создать таблицу для льготных кредитов"""
    try:
        async with async_session_factory() as session:
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS preferential_loans (
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
            return {"status": "success", "message": "✅ Таблица preferential_loans создана!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
# ===========================================
# ТЕСТОВЫЕ ДАННЫЕ ДЛЯ НОВЫХ ТАБЛИЦ
# ===========================================

@app.get("/api/seed-mortgage")
async def seed_mortgage():
    """Добавить тестовые ипотечные кредиты"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM mortgage_loans"))
            if result.scalar() == 0:
                await session.execute(text("""
                    INSERT INTO mortgage_loans (name, rate, term, amount, advantage, details) VALUES
                    ('Ипотека на новостройку', 'от 12.5%', 'до 20 лет', 'до 200 000 BYN', 
                     'Первоначальный взнос от 10%', 'Покупка квартиры в новостройке от застройщиков-партнеров'),
                    
                    ('Ипотека на вторичное жилье', 'от 13.9%', 'до 15 лет', 'до 150 000 BYN', 
                     'Быстрое оформление', 'Покупка готовой квартиры или дома на вторичном рынке'),
                    
                    ('Ипотека на дом с участком', 'от 14.5%', 'до 20 лет', 'до 250 000 BYN', 
                     'С возможностью покупки земельного участка', 'Кредит на строительство или покупку частного дома')
                """))
                await session.commit()
                return {"status": "success", "message": "✅ Тестовые ипотечные кредиты добавлены!", "count": 3}
            else:
                return {"status": "info", "message": f"ℹ️ В таблице уже есть {result.scalar()} записей"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/seed-preferential")
async def seed_preferential():
    """Добавить тестовые льготные кредиты"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM preferential_loans"))
            if result.scalar() == 0:
                await session.execute(text("""
                    INSERT INTO preferential_loans (name, rate, term, amount, advantage, details) VALUES
                    ('Для молодых семей', 'от 4.5%', 'до 10 лет', 'до 70 000 BYN', 
                     'Господдержка для молодых семей', 'Специальные условия при рождении ребенка. Первоначальный взнос от 5%'),
                    
                    ('Для предпринимателей', 'от 5.9%', 'до 5 лет', 'до 50 000 BYN', 
                     'На развитие бизнеса', 'Для ИП и владельцев малого бизнеса. Без залога при сумме до 30 000 BYN'),
                    
                    ('Для пенсионеров', 'от 6.5%', 'до 3 лет', 'до 10 000 BYN', 
                     'Льготные условия для пожилых', 'С пониженной процентной ставкой и упрощенным оформлением'),
                    
                    ('Для многодетных семей', 'от 3.9%', 'до 15 лет', 'до 100 000 BYN', 
                     'Государственная поддержка', 'Специальная программа для семей с тремя и более детьми')
                """))
                await session.commit()
                return {"status": "success", "message": "✅ Тестовые льготные кредиты добавлены!", "count": 4}
            else:
                return {"status": "info", "message": f"ℹ️ В таблице уже есть {result.scalar()} записей"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ===========================================
# API ДЛЯ ИПОТЕЧНЫХ КРЕДИТОВ (CRUD)
# ===========================================

# ПОЛУЧИТЬ ВСЕ ИПОТЕЧНЫЕ КРЕДИТЫ
@app.get("/api/mortgage-loans")
async def get_mortgage_loans():
    """Получить все ипотечные кредиты"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(
                text("SELECT id, name, rate, term, amount, advantage, details FROM mortgage_loans ORDER BY id")
            )
            rows = result.mappings().all()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error: {e}")
        return []

# ПОЛУЧИТЬ ИПОТЕЧНЫЙ КРЕДИТ ПО ID
@app.get("/api/mortgage-loans/{loan_id}")
async def get_mortgage_loan(loan_id: int):
    """Получить ипотечный кредит по ID"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(
                text("SELECT * FROM mortgage_loans WHERE id = :id"),
                {"id": loan_id}
            )
            loan = result.mappings().first()
            if not loan:
                raise HTTPException(status_code=404, detail="Кредит не найден")
            return dict(loan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ДОБАВИТЬ НОВЫЙ ИПОТЕЧНЫЙ КРЕДИТ
@app.post("/api/mortgage-loans")
async def create_mortgage_loan(loan: LoanCreate):
    """Добавить новый ипотечный кредит"""
    try:
        async with async_session_factory() as session:
            await session.execute(text("""
                INSERT INTO mortgage_loans (name, rate, term, amount, advantage, details)
                VALUES (:name, :rate, :term, :amount, :advantage, :details)
            """), loan.model_dump())
            await session.commit()
            return {"status": "success", "message": "✅ Ипотечный кредит успешно добавлен"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# УДАЛИТЬ ИПОТЕЧНЫЙ КРЕДИТ
@app.delete("/api/mortgage-loans/{loan_id}")
async def delete_mortgage_loan(loan_id: int):
    """Удалить ипотечный кредит"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(text("""
                DELETE FROM mortgage_loans WHERE id = :id
            """), {"id": loan_id})
            await session.commit()
            
            if result.rowcount == 0:
                return {"status": "error", "message": "❌ Кредит не найден"}
            return {"status": "success", "message": "✅ Кредит удален"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ===========================================
# API ДЛЯ ЛЬГОТНЫХ КРЕДИТОВ (CRUD)
# ===========================================

# ПОЛУЧИТЬ ВСЕ ЛЬГОТНЫЕ КРЕДИТЫ
@app.get("/api/preferential-loans")
async def get_preferential_loans():
    """Получить все льготные кредиты"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(
                text("SELECT id, name, rate, term, amount, advantage, details FROM preferential_loans ORDER BY id")
            )
            rows = result.mappings().all()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error: {e}")
        return []

# ПОЛУЧИТЬ ЛЬГОТНЫЙ КРЕДИТ ПО ID
@app.get("/api/preferential-loans/{loan_id}")
async def get_preferential_loan(loan_id: int):
    """Получить льготный кредит по ID"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(
                text("SELECT * FROM preferential_loans WHERE id = :id"),
                {"id": loan_id}
            )
            loan = result.mappings().first()
            if not loan:
                raise HTTPException(status_code=404, detail="Кредит не найден")
            return dict(loan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ДОБАВИТЬ НОВЫЙ ЛЬГОТНЫЙ КРЕДИТ
@app.post("/api/preferential-loans")
async def create_preferential_loan(loan: LoanCreate):
    """Добавить новый льготный кредит"""
    try:
        async with async_session_factory() as session:
            await session.execute(text("""
                INSERT INTO preferential_loans (name, rate, term, amount, advantage, details)
                VALUES (:name, :rate, :term, :amount, :advantage, :details)
            """), loan.model_dump())
            await session.commit()
            return {"status": "success", "message": "✅ Льготный кредит успешно добавлен"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# УДАЛИТЬ ЛЬГОТНЫЙ КРЕДИТ
@app.delete("/api/preferential-loans/{loan_id}")
async def delete_preferential_loan(loan_id: int):
    """Удалить льготный кредит"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(text("""
                DELETE FROM preferential_loans WHERE id = :id
            """), {"id": loan_id})
            await session.commit()
            
            if result.rowcount == 0:
                return {"status": "error", "message": "❌ Кредит не найден"}
            return {"status": "success", "message": "✅ Кредит удален"}
    except Exception as e:
        return {"status": "error", "message": str(e)}    

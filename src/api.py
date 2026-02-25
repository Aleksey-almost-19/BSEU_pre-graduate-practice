from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
import os
import sys
import json
import traceback

# ===========================================
# ИМПОРТЫ ИЗ ПРОЕКТА
# ===========================================
sys.path.append(os.path.dirname(__file__))
from database import async_session_factory

app = FastAPI()

# ===========================================
# НАСТРОЙКА CORS
# ===========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================================
# МОДЕЛИ ДАННЫХ
# ===========================================

class LoanCreate(BaseModel):
    name: str
    rate: str
    term: str
    amount: str
    advantage: list[str]
    details: str

class ContactRequest(BaseModel):
    telegram_id: int
    username: str = ""
    first_name: str = ""
    last_name: str = ""

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

@app.get("/mortgage_loans.html")
async def serve_mortgage_loans():
    return FileResponse("mortgage_loans.html")

@app.get("/preferential_loans.html")
async def serve_preferential_loans():
    return FileResponse("preferential_loans.html")

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
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ===========================================

async def create_loan_table(table_name: str):
    """Общая функция для создания таблиц с JSONB полем advantage"""
    async with async_session_factory() as session:
        await session.execute(text(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                rate VARCHAR(50) NOT NULL,
                term VARCHAR(50) NOT NULL,
                amount VARCHAR(50) NOT NULL,
                advantage JSONB NOT NULL DEFAULT '[]'::jsonb,
                details TEXT NOT NULL
            )
        """))
        await session.commit()

def safe_json_loads(data):
    """Безопасно загружает JSON, возвращает список"""
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, str):
        try:
            return json.loads(data)
        except:
            return [data]
    return [str(data)]

# ===========================================
# УПРАВЛЕНИЕ БАЗОЙ ДАННЫХ (СОЗДАНИЕ ТАБЛИЦ)
# ===========================================

@app.get("/api/create-tables")
async def create_tables():
    """Создать таблицу consumer_loans с JSONB"""
    try:
        await create_loan_table("consumer_loans")
        return {"status": "success", "message": "✅ Таблица consumer_loans создана с поддержкой JSONB!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/create-mortgage-table")
async def create_mortgage_table():
    """Создать таблицу mortgage_loans с JSONB"""
    try:
        await create_loan_table("mortgage_loans")
        return {"status": "success", "message": "✅ Таблица mortgage_loans создана с поддержкой JSONB!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/create-preferential-table")
async def create_preferential_table():
    """Создать таблицу preferential_loans с JSONB"""
    try:
        await create_loan_table("preferential_loans")
        return {"status": "success", "message": "✅ Таблица preferential_loans создана с поддержкой JSONB!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/create-contacts-table")
async def create_contacts_table():
    """Создать таблицу для заявок"""
    try:
        async with async_session_factory() as session:
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS contact_requests (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT NOT NULL,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    last_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    status VARCHAR(50) DEFAULT 'new'
                )
            """))
            await session.commit()
            return {"status": "success", "message": "✅ Таблица contact_requests создана!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ===========================================
# ТЕСТОВЫЕ ДАННЫЕ
# ===========================================

@app.get("/api/seed-database")
async def seed_database():
    """Добавить тестовые потребительские кредиты с JSONB"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM consumer_loans"))
            count = result.scalar()
            
            if count == 0:
                await session.execute(text("""
                    INSERT INTO consumer_loans (name, rate, term, amount, advantage, details) VALUES
                    ('Кредит на любые цели', 'от 11.9%', 'до 7 лет', 'до 15 000 BYN', 
                     :adv1, 
                     'Кредит без залога и поручителей. Минимальный пакет документов — только паспорт.'),
                    
                    ('Кредит для зарплатных клиентов', 'от 10.5%', 'до 5 лет', 'до 20 000 BYN', 
                     :adv2, 
                     'Для клиентов, получающих зарплату на карту Аурумбанка. Сниженная процентная ставка.'),
                    
                    ('Рефинансирование кредитов', 'от 11.5%', 'до 10 лет', 'до 50 000 BYN', 
                     :adv3, 
                     'Рефинансирование кредитов других банков. Снижение ежемесячного платежа.')
                """),
                {
                    "adv1": json.dumps(["Без справок о доходах", "Решение за 15 минут", "Онлайн-оформление"]),
                    "adv2": json.dumps(["Специальные условия", "Сниженная ставка", "Быстрое одобрение"]),
                    "adv3": json.dumps(["Объедините несколько кредитов", "Снижение платежа", "Увеличение срока"])
                })
                await session.commit()
                return {"status": "success", "message": "✅ Тестовые потребительские кредиты добавлены с JSONB!", "count": 3}
            else:
                return {"status": "info", "message": f"ℹ️ В таблице уже есть {count} записей", "count": count}
    except Exception as e:
        print(f"Error in seed_database: {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/api/seed-mortgage")
async def seed_mortgage():
    """Добавить тестовые ипотечные кредиты с JSONB"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM mortgage_loans"))
            count = result.scalar()
            
            if count == 0:
                await session.execute(text("""
                    INSERT INTO mortgage_loans (name, rate, term, amount, advantage, details) VALUES
                    ('Ипотека на новостройку', 'от 12.5%', 'до 20 лет', 'до 200 000 BYN', 
                     :adv1, 
                     'Покупка квартиры в новостройке от застройщиков-партнеров'),
                    
                    ('Ипотека на вторичное жилье', 'от 13.9%', 'до 15 лет', 'до 150 000 BYN', 
                     :adv2, 
                     'Покупка готовой квартиры или дома на вторичном рынке'),
                    
                    ('Ипотека на дом с участком', 'от 14.5%', 'до 20 лет', 'до 250 000 BYN', 
                     :adv3, 
                     'Кредит на строительство или покупку частного дома')
                """),
                {
                    "adv1": json.dumps(["Первоначальный взнос от 10%", "Господдержка", "Страхование опционально"]),
                    "adv2": json.dumps(["Быстрое оформление", "Без скрытых комиссий", "Оценка бесплатно"]),
                    "adv3": json.dumps(["С возможностью покупки участка", "Длительный срок", "Индивидуальные условия"])
                })
                await session.commit()
                return {"status": "success", "message": "✅ Тестовые ипотечные кредиты добавлены с JSONB!", "count": 3}
            else:
                return {"status": "info", "message": f"ℹ️ В таблице уже есть {count} записей"}
    except Exception as e:
        print(f"Error in seed_mortgage: {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.get("/api/seed-preferential")
async def seed_preferential():
    """Добавить тестовые льготные кредиты с JSONB"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM preferential_loans"))
            count = result.scalar()
            
            if count == 0:
                await session.execute(text("""
                    INSERT INTO preferential_loans (name, rate, term, amount, advantage, details) VALUES
                    ('Для молодых семей', 'от 4.5%', 'до 10 лет', 'до 70 000 BYN', 
                     :adv1, 
                     'Специальные условия при рождении ребенка. Первоначальный взнос от 5%'),
                    
                    ('Для предпринимателей', 'от 5.9%', 'до 5 лет', 'до 50 000 BYN', 
                     :adv2, 
                     'Для ИП и владельцев малого бизнеса. Без залога при сумме до 30 000 BYN'),
                    
                    ('Для пенсионеров', 'от 6.5%', 'до 3 лет', 'до 10 000 BYN', 
                     :adv3, 
                     'С пониженной процентной ставкой и упрощенным оформлением'),
                    
                    ('Для многодетных семей', 'от 3.9%', 'до 15 лет', 'до 100 000 BYN', 
                     :adv4, 
                     'Специальная программа для семей с тремя и более детьми')
                """),
                {
                    "adv1": json.dumps(["Господдержка", "Льготная ставка", "Отсрочка платежа"]),
                    "adv2": json.dumps(["На развитие бизнеса", "Без залога", "Быстрое решение"]),
                    "adv3": json.dumps(["Льготные условия", "Упрощенное оформление", "Пониженная ставка"]),
                    "adv4": json.dumps(["Государственная поддержка", "Длительный срок", "Субсидии"])
                })
                await session.commit()
                return {"status": "success", "message": "✅ Тестовые льготные кредиты добавлены с JSONB!", "count": 4}
            else:
                return {"status": "info", "message": f"ℹ️ В таблице уже есть {count} записей"}
    except Exception as e:
        print(f"Error in seed_preferential: {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

# ===========================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ КРЕДИТОВ
# ===========================================

async def get_loans(table_name: str):
    """Общая функция для получения кредитов из любой таблицы"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(
                text(f"SELECT id, name, rate, term, amount, advantage, details FROM {table_name} ORDER BY id")
            )
            rows = result.mappings().all()
            
            loans = []
            for row in rows:
                loan_dict = dict(row)
                loan_dict["advantage"] = safe_json_loads(loan_dict.get("advantage"))
                loans.append(loan_dict)
            
            return loans
    except Exception as e:
        print(f"Error in get_loans for {table_name}: {e}")
        traceback.print_exc()
        return []

async def get_loan_by_id(table_name: str, loan_id: int):
    """Общая функция для получения кредита по ID"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(
                text(f"SELECT * FROM {table_name} WHERE id = :id"),
                {"id": loan_id}
            )
            row = result.mappings().first()
            if not row:
                return None
            loan_dict = dict(row)
            loan_dict["advantage"] = safe_json_loads(loan_dict.get("advantage"))
            return loan_dict
    except Exception as e:
        print(f"Error in get_loan_by_id for {table_name}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ===========================================
# API ДЛЯ ПОТРЕБИТЕЛЬСКИХ КРЕДИТОВ
# ===========================================

@app.get("/api/consumer-loans")
async def get_all_consumer_loans():
    """Получить все потребительские кредиты"""
    return await get_loans("consumer_loans")

@app.get("/api/consumer-loans/{loan_id}")
async def get_consumer_loan(loan_id: int):
    """Получить потребительский кредит по ID"""
    loan = await get_loan_by_id("consumer_loans", loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Кредит не найден")
    return loan

@app.post("/api/consumer-loans")
async def create_consumer_loan(loan: LoanCreate):
    """Добавить новый потребительский кредит"""
    try:
        async with async_session_factory() as session:
            # Преобразуем список преимуществ в JSON-строку
            advantages_json = json.dumps(loan.advantage, ensure_ascii=False)
            
            await session.execute(text("""
                INSERT INTO consumer_loans (name, rate, term, amount, advantage, details)
                VALUES (:name, :rate, :term, :amount, :advantage::jsonb, :details)
            """), {
                "name": loan.name,
                "rate": loan.rate,
                "term": loan.term,
                "amount": loan.amount,
                "advantage": advantages_json,
                "details": loan.details
            })
            await session.commit()
            return {"status": "success", "message": "✅ Потребительский кредит успешно добавлен"}
    except Exception as e:
        print(f"Error in create_consumer_loan: {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

@app.delete("/api/consumer-loans/{loan_id}")
async def delete_consumer_loan(loan_id: int):
    """Удалить потребительский кредит"""
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
        print(f"Error in delete_consumer_loan: {e}")
        return {"status": "error", "message": str(e)}

# ===========================================
# API ДЛЯ ИПОТЕЧНЫХ КРЕДИТОВ
# ===========================================

@app.get("/api/mortgage-loans")
async def get_all_mortgage_loans():
    """Получить все ипотечные кредиты"""
    return await get_loans("mortgage_loans")

@app.get("/api/mortgage-loans/{loan_id}")
async def get_mortgage_loan(loan_id: int):
    """Получить ипотечный кредит по ID"""
    loan = await get_loan_by_id("mortgage_loans", loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Кредит не найден")
    return loan

@app.post("/api/mortgage-loans")
async def create_mortgage_loan(loan: LoanCreate):
    """Добавить новый ипотечный кредит"""
    try:
        async with async_session_factory() as session:
            advantages_json = json.dumps(loan.advantage, ensure_ascii=False)
            
            await session.execute(text("""
                INSERT INTO mortgage_loans (name, rate, term, amount, advantage, details)
                VALUES (:name, :rate, :term, :amount, :advantage::jsonb, :details)
            """), {
                "name": loan.name,
                "rate": loan.rate,
                "term": loan.term,
                "amount": loan.amount,
                "advantage": advantages_json,
                "details": loan.details
            })
            await session.commit()
            return {"status": "success", "message": "✅ Ипотечный кредит успешно добавлен"}
    except Exception as e:
        print(f"Error in create_mortgage_loan: {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

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
        print(f"Error in delete_mortgage_loan: {e}")
        return {"status": "error", "message": str(e)}

# ===========================================
# API ДЛЯ ЛЬГОТНЫХ КРЕДИТОВ
# ===========================================

@app.get("/api/preferential-loans")
async def get_all_preferential_loans():
    """Получить все льготные кредиты"""
    return await get_loans("preferential_loans")

@app.get("/api/preferential-loans/{loan_id}")
async def get_preferential_loan(loan_id: int):
    """Получить льготный кредит по ID"""
    loan = await get_loan_by_id("preferential_loans", loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Кредит не найден")
    return loan

@app.post("/api/preferential-loans")
async def create_preferential_loan(loan: LoanCreate):
    """Добавить новый льготный кредит"""
    try:
        async with async_session_factory() as session:
            advantages_json = json.dumps(loan.advantage, ensure_ascii=False)
            
            await session.execute(text("""
                INSERT INTO preferential_loans (name, rate, term, amount, advantage, details)
                VALUES (:name, :rate, :term, :amount, :advantage::jsonb, :details)
            """), {
                "name": loan.name,
                "rate": loan.rate,
                "term": loan.term,
                "amount": loan.amount,
                "advantage": advantages_json,
                "details": loan.details
            })
            await session.commit()
            return {"status": "success", "message": "✅ Льготный кредит успешно добавлен"}
    except Exception as e:
        print(f"Error in create_preferential_loan: {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

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
        print(f"Error in delete_preferential_loan: {e}")
        return {"status": "error", "message": str(e)}

# ===========================================
# API ДЛЯ ЗАЯВОК
# ===========================================

@app.post("/api/contact-request")
async def save_contact_request(request: ContactRequest):
    """Сохранить заявку с Telegram ID"""
    try:
        async with async_session_factory() as session:
            await session.execute(text("""
                INSERT INTO contact_requests (telegram_id, username, first_name, last_name, status)
                VALUES (:telegram_id, :username, :first_name, :last_name, 'new')
            """), {
                "telegram_id": request.telegram_id,
                "username": request.username,
                "first_name": request.first_name,
                "last_name": request.last_name
            })
            await session.commit()
            
            return {
                "status": "success", 
                "message": "✅ Заявка сохранена! Менеджер свяжется с вами.",
                "telegram_id": request.telegram_id
            }
    except Exception as e:
        print(f"Error in save_contact_request: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/contact-requests")
async def get_contact_requests():
    """Получить все заявки"""
    try:
        async with async_session_factory() as session:
            result = await session.execute(
                text("SELECT * FROM contact_requests ORDER BY created_at DESC")
            )
            rows = result.mappings().all()
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error in get_contact_requests: {e}")
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
        "version": "5.0.0"
    }
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from database import async_session_factory
from models import ConsumerLoan
import uvicorn
from typing import List

app = FastAPI(title="AurumBank API")

# CORS для Telegram Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/consumer-loans", response_model=List[dict])
async def get_consumer_loans():
    """Получить все потребительские кредиты"""
    async with async_session_factory() as session:
        result = await session.execute(
            text("SELECT * FROM consumer_loans ORDER BY id")
        )
        loans = result.mappings().all()
        return [dict(loan) for loan in loans]

@app.get("/api/consumer-loans/{loan_id}")
async def get_consumer_loan(loan_id: int):
    """Получить конкретный кредит"""
    async with async_session_factory() as session:
        result = await session.execute(
            text("SELECT * FROM consumer_loans WHERE id = :id"),
            {"id": loan_id}
        )
        loan = result.mappings().first()
        if not loan:
            raise HTTPException(status_code=404, detail="Кредит не найден")
        return dict(loan)

@app.on_event("startup")
async def init_data():
    """Заполнить БД тестовыми данными при запуске"""
    async with async_session_factory() as session:
        # Проверим есть ли данные
        result = await session.execute(
            text("SELECT COUNT(*) FROM consumer_loans")
        )
        count = result.scalar()
        
        if count == 0:
            # Добавляем тестовые данные
            loans_data = [
                {
                    "name": "Кредит на любые цели",
                    "rate": "от 11.9%",
                    "term": "до 7 лет",
                    "amount": "до 15 000 BYN",
                    "advantage": "Без справок о доходах, решение за 15 минут",
                    "details": "Кредит без залога и поручителей. Сумма до 15 000 BYN на срок до 7 лет. Минимальный пакет документов — только паспорт."
                },
                {
                    "name": "Кредит для зарплатных клиентов",
                    "rate": "от 10.5%",
                    "term": "до 5 лет",
                    "amount": "до 20 000 BYN",
                    "advantage": "Специальные условия для зарплатных клиентов",
                    "details": "Для клиентов, получающих зарплату на карту Аурумбанка. Сниженная процентная ставка, ускоренное рассмотрение."
                },
                {
                    "name": "Рефинансирование кредитов",
                    "rate": "от 11.5%",
                    "term": "до 10 лет",
                    "amount": "до 50 000 BYN",
                    "advantage": "Объедините несколько кредитов в один",
                    "details": "Рефинансирование кредитов других банков. Снижение ежемесячного платежа, увеличение срока кредитования."
                },
                {
                    "name": "Экспресс-кредит",
                    "rate": "от 13.9%",
                    "term": "до 3 лет",
                    "amount": "до 5 000 BYN",
                    "advantage": "Решение за 5 минут, деньги сразу",
                    "details": "Микрокредит на неотложные нужды. Быстрое оформление через интернет-банкинг."
                },
                {
                    "name": "Кредит на образование",
                    "rate": "от 9.9%",
                    "term": "до 11 лет",
                    "amount": "до 25 000 BYN",
                    "advantage": "Льготный период на время обучения",
                    "details": "Кредит на оплату обучения в вузах и колледжах. Отсрочка погашения основного долга на время учебы."
                }
            ]
            
            for loan in loans_data:
                await session.execute(
                    text("""
                        INSERT INTO consumer_loans 
                        (name, rate, term, amount, advantage, details) 
                        VALUES (:name, :rate, :term, :amount, :advantage, :details)
                    """),
                    loan
                )
            await session.commit()
            print("✅ Тестовые кредиты добавлены в БД")

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
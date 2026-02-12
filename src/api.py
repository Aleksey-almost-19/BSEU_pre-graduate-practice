from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "AurumBank API is working!", "status": "ok"}

@app.get("/api/consumer-loans")
async def get_consumer_loans():
    
    return [{"id": 1, "name": "Тестовый кредит", "rate": "от 11.9%"}]
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text
from database import Base

class ConsumerLoan(Base):
    __tablename__ = "consumer_loans"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))  # Название кредита
    rate: Mapped[str] = mapped_column(String(50))   # Ставка/проценты
    term: Mapped[str] = mapped_column(String(50))   # Срок кредита
    amount: Mapped[str] = mapped_column(String(50)) # Сумма
    advantage: Mapped[str] = mapped_column(Text)    # Преимущества
    details: Mapped[str] = mapped_column(Text)      # Детальное описание
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "rate": self.rate,
            "term": self.term,
            "amount": self.amount,
            "advantage": self.advantage,
            "details": self.details
        }
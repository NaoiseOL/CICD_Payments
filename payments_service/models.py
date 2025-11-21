from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey

class Base(DeclarativeBase):
    pass

class PaymentsDB(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    card_no: Mapped[str] = mapped_column(String(100), nullable=False)
    expiry: Mapped[str] = mapped_column(String(100), nullable=False)
    nameOnCard: Mapped[str] = mapped_column(String(100), nullable=False)
    CVV: Mapped[str] = mapped_column(String(100), nullable=False)
    billing_address: Mapped[str] = mapped_column(String(100), nullable=False)
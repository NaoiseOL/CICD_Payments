from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey


class Base(DeclarativeBase):
    pass
    
class UserDB(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    surname: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    phoneNo: Mapped[str] = mapped_column(unique=True, nullable=False)
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .database import engine, SessionLocal
from .models import Base, PaymentsDB
from .schemas import PaymentCreate, PaymentRead

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

# CORS (add this block)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # dev-friendly; tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/payments", response_model=list[PaymentRead])
def list_payments(db: Session = Depends(get_db)):
    stmt = select(PaymentsDB).order_by(PaymentsDB.payment_id)
    result = db.execute(stmt)
    payments = result.scalars().all()
    return payments


@app.get("/api/payments/{payments_id}", response_model=PaymentRead)
def get_payments(payments_id: int, db: Session = Depends(get_db)):
    payment = db.get(PaymentsDB, payments_id)
    if not payment:
        raise HTTPException(status_code=404, detail="payment not found")
    return payment


@app.post("/api/payments", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def add_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    payment = PaymentsDB(**payload.dict(exclude_unset=True))
    db.add(payment)
    try:
        db.commit()
        db.refresh(payment)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Payment already exists")
    return payment

@app.put("/api/payments/{payments_id}", response_model=PaymentRead)
def replace_payment(payments_id: int, payload: PaymentCreate, db: Session = Depends(get_db)):
    payments = db.get(PaymentsDB, payments_id)
    if not payments:
        raise HTTPException(status_code=404, detail="payments not found")

    payments.card_no = payload.card_no
    payments.expiry = payload.expiry
    payments.nameOnCard = payload.nameOnCard
    payments.CVV = payload.CVV
    payments.billing_address = payload.billing_address

    try:
        db.commit()
        db.refresh(payments)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="payment update Failed")
    return payments

@app.delete("/api/payments/{payments_id}", status_code=204)
def delete_payments(payments_id: int, db: Session = Depends(get_db)) -> Response:
    payments = db.get(PaymentsDB, payments_id)
    if not payments:
        raise HTTPException(status_code=404, detail="payments not found")
    db.delete_payments
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
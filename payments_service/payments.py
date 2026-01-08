from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .database import engine, SessionLocal
from .models import Base, PaymentsDB
from .schemas import PaymentCreate, PaymentRead, PaymentUpdate
from .rabbit import publish_event
import asyncio

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
async def add_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    payment = PaymentsDB(**payload.dict(exclude_unset=True))
    db.add(payment)
    try:
        db.commit()
        db.refresh(payment)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Payment already exists")

    asyncio.create_task(
        publish_event(
            "payment.created",
            {
                "id": payment.payment_id,
                "nameOnCard": payment.nameOnCard,
                "billing_address": payment.billing_address
            }
        )
    )
    
    return payment

@app.put("/api/payments/{payment_id}", response_model=PaymentRead)
async def replace_payment(payment_id: int, payload: PaymentCreate, db: Session = Depends(get_db)):
    payment = db.get(PaymentsDB, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="payments not found")

    payment.card_no = payload.card_no
    payment.expiry = payload.expiry
    payment.nameOnCard = payload.nameOnCard
    payment.CVV = payload.CVV
    payment.billing_address = payload.billing_address

    try:
        db.commit()
        db.refresh(payment)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="payment update Failed")

    asyncio.create_task(
        publish_event(
            "payment.updated",
            {
                "id": payment.payment_id,
                "nameOnCard": payment.nameOnCard,
                "billing_address": payment.billing_address
            }
        )
    )

    return payment

@app.delete("/api/payments/{payment_id}", status_code=204)
async def delete_payment(payment_id: int, db: Session = Depends(get_db)) -> Response:
    payment = db.get(PaymentsDB, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="payment not found")

    asyncio.create_task(
        publish_event(
            "payment.deleted",
            {
                "id": payment.payment_id,
                "nameOnCard": payment.nameOnCard,
                "billing_address": payment.billing_address
            }
        )
    )

    db.delete(payment)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.patch("/api/payments/{payment_id}", response_model=PaymentRead)
async def patch_payment(payment_id: int, payload: PaymentUpdate, db: Session = Depends(get_db)):
    payment = db.get(PaymentsDB, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment Not Found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(payment, field, value)

    try:
        db.commit()
        db.refresh(payment)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Payment Patch failed")

    asyncio.create_task(
        publish_event(
            "payment.patched",
            {
                "id": payment.payment_id,
                "nameOnCard": payment.nameOnCard,
                "billing_address": payment.billing_address
            }
        )
    )

    return payment
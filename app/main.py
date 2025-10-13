from fastapi import FastAPI
from app.bookings import router as booking_router
from app.users import router as users_router
from app.payments import router as payments_router

app = FastAPI()

app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(booking_router, prefix="/api/bookings", tags=["Bookings"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])
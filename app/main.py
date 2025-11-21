from fastapi import FastAPI
from bookings_service.bookings import app as booking_app
from users_service.users import app as users_app
from payments_service.payments import app as payments_app

app = FastAPI()

app.mount("/api/users", users_app)
app.mount("/api/bookings", booking_app)
app.mount("/api/payments", payments_app)
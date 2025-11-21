from typing import Annotated, Optional, List
from annotated_types import Ge, Le
from pydantic import BaseModel, EmailStr, Field, StringConstraints, ConfigDict

booking_numberStr = Annotated[str, StringConstraints(min_length=2, max_length=50)]
nameOnCardStr = Annotated[str, StringConstraints(min_length=2, max_length=50)]
card_noStr = Annotated[str, StringConstraints(min_length=2, max_length=50)]
expiryStr = Annotated[str, StringConstraints(min_length=2, max_length=50)]
CVVStr = Annotated[str, StringConstraints(min_length=2, max_length=50)]
billing_addressStr = Annotated[str, StringConstraints(min_length=2, max_length=50)]

class PaymentCreate(BaseModel):
    payment_id: int
    card_no: card_noStr
    expiry: expiryStr
    nameOnCard: nameOnCardStr
    CVV: CVVStr
    billing_address: billing_addressStr

class PaymentRead(BaseModel):
    payment_id: int
    card_no: card_noStr
    expiry: expiryStr
    nameOnCard: nameOnCardStr
    CVV: CVVStr
    billing_address: billing_addressStr

    model_config = ConfigDict(from_attributes=True)
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.order import OrderStatus, PaymentMethod


class OrderCreate(BaseModel):
    product_id: int
    buyer_email: EmailStr
    payment_method: PaymentMethod
    remark: str | None = Field(default=None, max_length=500)


class PaymentInstruction(BaseModel):
    method: PaymentMethod
    label: str
    qr_code_url: str
    account_hint: str


class OrderRead(BaseModel):
    id: int
    order_no: str
    product_id: int
    product_name: str
    buyer_email: EmailStr | None = None
    payment_method: PaymentMethod
    amount_cents: int
    currency: str
    remark: str | None
    status: OrderStatus
    created_at: datetime
    paid_confirmed_at: datetime | None = None
    payment_instruction: PaymentInstruction


class OrderConfirmResponse(BaseModel):
    order: OrderRead
    notification_sent: bool
    notification_channel: str

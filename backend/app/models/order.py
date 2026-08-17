from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PaymentMethod(str, Enum):
    alipay = "alipay"
    wechat = "wechat"


class OrderStatus(str, Enum):
    pending = "pending"
    paid_confirmed = "paid_confirmed"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    buyer_email: Mapped[str] = mapped_column(String(255), nullable=True)
    payment_method: Mapped[str] = mapped_column(String(24), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(12), default="CNY", nullable=False)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default=OrderStatus.pending.value, nullable=False)
    paid_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="orders")

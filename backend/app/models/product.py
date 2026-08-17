from datetime import datetime

from enum import IntEnum
from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProductSaleStatus(IntEnum):
    on_sale = 1
    restocking = 2
    discontinued = 3


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    summary: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(12), default="CNY", nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_hint: Mapped[str] = mapped_column(String(255), nullable=False)
    notification_email: Mapped[str] = mapped_column(String(255), nullable=False)
    sale_status: Mapped[int] = mapped_column(Integer, default=ProductSaleStatus.on_sale.value, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="product")

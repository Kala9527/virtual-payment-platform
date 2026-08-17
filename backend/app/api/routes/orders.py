from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.order import OrderConfirmResponse, OrderCreate, OrderRead
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=201)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> OrderRead:
    return OrderService(db, settings).create_order(payload)


@router.post("/{order_no}/confirm", response_model=OrderConfirmResponse)
def confirm_payment(
    order_no: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> OrderConfirmResponse:
    return OrderService(db, settings).confirm_payment(order_no)


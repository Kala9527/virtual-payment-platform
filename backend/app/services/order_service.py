from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.order import Order, OrderStatus, PaymentMethod
from app.models.product import ProductSaleStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import OrderConfirmResponse, OrderCreate, OrderRead
from app.services.email_service import EmailService
from app.services.payment_service import PaymentInstructionService


class OrderService:
    def __init__(self, db: Session, settings: Settings):
        self.products = ProductRepository(db)
        self.orders = OrderRepository(db)
        self.payment_instructions = PaymentInstructionService()
        self.email = EmailService(settings)

    def create_order(self, payload: OrderCreate) -> OrderRead:
        product = self.products.get_by_id(payload.product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品不存在")

        if product.sale_status != ProductSaleStatus.on_sale.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="商品当前不可购买")

        order = Order(
            order_no=self._generate_order_no(),
            product_id=product.id,
            buyer_email=str(payload.buyer_email),
            payment_method=payload.payment_method.value,
            amount_cents=product.price_cents,
            currency=product.currency,
            remark=payload.remark,
        )
        saved = self.orders.add(order)
        saved.product = product
        self.email.send_payment_confirmation(
            recipient=saved.product.notification_email,
            subject=self._build_notification_subject(saved, "已下单"),
            body=self._build_notification_body(saved, "下单", saved.created_at),
        )
        return self._to_read(saved)

    def confirm_payment(self, order_no: str) -> OrderConfirmResponse:
        order = self.orders.get_by_order_no(order_no)
        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单不存在")

        if order.status != OrderStatus.paid_confirmed.value:
            order.status = OrderStatus.paid_confirmed.value
            order.paid_confirmed_at = datetime.utcnow()
            order = self.orders.save(order)

        result = self.email.send_payment_confirmation(
            recipient=order.product.notification_email,
            subject=self._build_notification_subject(order, "已支付"),
            body=self._build_notification_body(
                order,
                "支付",
                order.paid_confirmed_at or datetime.utcnow(),
            ),
        )
        return OrderConfirmResponse(
            order=self._to_read(order),
            notification_sent=result.sent,
            notification_channel=result.channel,
        )

    def _to_read(self, order: Order) -> OrderRead:
        method = PaymentMethod(order.payment_method)
        return OrderRead(
            id=order.id,
            order_no=order.order_no,
            product_id=order.product_id,
            product_name=order.product.name,
            buyer_email=order.buyer_email or None,
            payment_method=method,
            amount_cents=order.amount_cents,
            currency=order.currency,
            remark=order.remark,
            status=OrderStatus(order.status),
            created_at=order.created_at,
            paid_confirmed_at=order.paid_confirmed_at,
            payment_instruction=self.payment_instructions.get_instruction(method),
        )

    def _generate_order_no(self) -> str:
        return f"VP{datetime.utcnow().strftime('%Y%m%d')}{uuid4().hex[:10].upper()}"

    def _build_notification_subject(self, order: Order, status_label: str) -> str:
        return f"{order.order_no}（{status_label}）"

    def _build_notification_body(
        self,
        order: Order,
        action_label: str,
        action_time: datetime,
    ) -> str:
        payment_method_labels = {
            PaymentMethod.alipay.value: "支付宝",
            PaymentMethod.wechat.value: "微信支付",
        }
        payment_method = payment_method_labels.get(order.payment_method, order.payment_method)
        formatted_time = action_time.strftime("%Y-%m-%d %H:%M:%S")
        remark = order.remark or ""
        buyer_email = order.buyer_email or ""
        return (
            f"订单号：{order.order_no}\n"
            f"{action_label}时间：{formatted_time}\n"
            f"支付方式：{payment_method}\n"
            f"联系方式：{buyer_email}\n"
            f"备注:{remark}"
        )
